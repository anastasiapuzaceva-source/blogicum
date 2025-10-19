from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse

from .models import Post, Comment
from .utils import get_posts_queryset


class PublishedPostMixin:
    def get_queryset(self):
        return get_posts_queryset(
            Post.objects,
            filter_published=True,
            annotate_comments=True
        )


class IsAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(
                f"{reverse_lazy('login')}?next={self.request.path}"
            )

        post_id = self.kwargs.get('post_id')
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
