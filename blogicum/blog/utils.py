from django.db.models import Count
from django.utils import timezone

from .models import Post


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
