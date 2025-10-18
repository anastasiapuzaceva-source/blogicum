from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from .models import Post, Comment


def get_posts_queryset(
        manager=Post.objects,
        filter_published=False,
        annotate_comments=False):
    queryset = manager.select_related('author', 'location', 'category')
    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    if annotate_comments:
        queryset = queryset.annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    return queryset


class PublishedPostMixin:
    def get_queryset(self):
        return get_posts_queryset(
            Post.objects,
            filter_published=True,
            annotate_comments=True
        )


class IsAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if 'comment_id' in self.kwargs:
            obj = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
        else:
            obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return obj.author == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(
                f"{reverse_lazy('login')}?next={self.request.path}"
            )

        post_id = self.kwargs.get('post_id')
        if not post_id and 'comment_id' in self.kwargs:
            comment = get_object_or_404(Comment, pk=self.kwargs['comment_id'])
            post_id = comment.post.pk
        return redirect('blog:post_detail', post_id=post_id)


class CommentMixin(IsAuthorMixin):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post__pk=self.kwargs['post_id'],
            author=self.request.user
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )
