from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import BlogPostForm, CommentForm, UserEditForm
from .models import Category, Comment, Post, Profile


POSTS_LIMIT = 10

class PublishedPostMixin:
    def get_queryset(self):
        basic_request = Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related(
            'author',
            'location',
            'category'
        ).annotate(
            comment_count=Count('comments')
        )
        return basic_request.order_by('-pub_date')


class UpdateMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(Post, pk=kwargs['pk'])
        if not request.user.is_authenticated:
            return redirect(f"{reverse_lazy('login')}?next={request.path}")
        elif obj.author != request.user:
            return redirect('blog:post_detail', pk=obj.pk)
        return super().dispatch(request, *args, **kwargs)


class IndexListView(PublishedPostMixin, ListView):
    model = Post
    ordering = ['-pub_date']
    paginate_by = POSTS_LIMIT
    template_name = 'blog/index.html'


class PostDetailView(PublishedPostMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['form'] = CommentForm()
        context['post'] = self.object
        context['comments'] = post.comments.order_by('created_at')
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        if not post.is_published or post.pub_date > timezone.now():
            if post.author != self.request.user:
                raise Http404
        if post.category and not post.category.is_published:
            if post.author != self.request.user:
                raise Http404
        return post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = BlogPostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateMixin, UpdateView):
    model = Post
    form_class = BlogPostForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form_class()()
        context['form'].instance = self.object
        return context

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])

        if not (post.author == request.user or request.user.is_staff):
            raise Http404("Удалять может только автор или администратор.")

        return super().dispatch(request, *args, **kwargs)




class CategoryPostListView(PublishedPostMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_LIMIT
    def get_queryset(self):
        queryset = super().get_queryset()
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )
        return queryset.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_obj.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user

class ProfileDetailView(PublishedPostMixin, DetailView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_LIMIT

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return get_object_or_404(Profile, user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        author = profile.user

        posts_list = (
            Post.objects.filter(author=author)
            .select_related('author', 'location', 'category')
            .annotate(comment_count=Count('comments'))
            .order_by('-pub_date')
        )

        if self.request.user != author and not self.request.user.is_staff:
            visible_posts = []
            for post in posts_list:
                if post.is_published and post.pub_date <= timezone.now():
                    if not post.category or post.category.is_published:
                        visible_posts.append(post)
            posts_list = visible_posts

        paginator = Paginator(posts_list, self.paginate_by)
        page_number = self.request.GET.get('page')

        context.update({
            'posts': posts_list,
            'page_obj': paginator.get_page(page_number),
            'profile': author,
        })
        return context