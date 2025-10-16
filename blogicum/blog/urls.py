from django.urls import path

from . import views
from .views import PostUpdateView, PostDeleteView

app_name = 'blog'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostListView.as_view(),
        name='category_posts'
    ),
    path('profile/edit/', views.ProfileEditView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),
    path('posts/<int:pk>/comment/', views.CommentCreateView.as_view(), name='add_comment'),
    path('posts/<int:pk>/edit/', PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='delete_post'),
    path('posts/<int:post_id>/edit_comment/<int:pk>/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<int:post_id>/delete_comment/<int:pk>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    path('posts/create', views.PostCreateView.as_view(), name='create_post'),
]
