from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import BlogPostForm, CommentForm, UserEditForm
from .mixin import PublishedPostMixin, IsAuthorMixin, CommentMixin
from .models import Category, Comment, Post
from .utils import get_posts_queryset


class IndexListView(PublishedPostMixin, ListView):
    model = Post
    ordering = ['-pub_date']
    paginate_by = settings.POSTS_LIMIT
    template_name = 'blog/index.html'


class PostDetailView(PublishedPostMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['form'] = CommentForm()
        context['comments'] = post.comments.order_by('created_at')
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(
            get_posts_queryset(filter_published=False),
            pk=self.kwargs['post_id']
        )
        if post.author != self.request.user:
            queryset = get_posts_queryset(filter_published=True)
            post = get_object_or_404(queryset, pk=self.kwargs['post_id'])

        return post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = BlogPostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(IsAuthorMixin, UpdateView):
    model = Post
    form_class = BlogPostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class PostDeleteView(IsAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BlogPostForm(instance=self.object)
        context['is_delete'] = True
        return context


class CategoryPostListView(PublishedPostMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = settings.POSTS_LIMIT

    def get_category(self):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True,
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.get_category()
        return queryset.filter(category=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'

    def form_valid(self, form, **kwargs):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        form.instance.author = self.request.user
        form.instance.post = post
        self.post = post
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.kwargs.get('post_id')
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class CommentUpdateView(CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentMixin, DeleteView):
    pass


class RegistrationCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset=None):
        return self.request.user


class ProfileDetailView(PublishedPostMixin, ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = settings.POSTS_LIMIT

    def get_profile_user(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_queryset(self):
        author = self.get_profile_user()
        queryset = get_posts_queryset(
            manager=author.posts,
            filter_published=self.request.user != author,
            annotate_comments=True
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile_user()
        return context
