from django.urls import path, include

from . import views

app_name = 'blog'


post_urls = [
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        '<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
]

profile_urls = [
    path(
        'edit/',
        views.ProfileEditView.as_view(),
        name='edit_profile'
    ),
    path(
        '<str:username>/',
        views.ProfileDetailView.as_view(),
        name='profile'
    ),
]

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostListView.as_view(),
        name='category_posts'
    ),
    path('posts/', include(post_urls)),
    path('profile/', include(profile_urls)),
]
