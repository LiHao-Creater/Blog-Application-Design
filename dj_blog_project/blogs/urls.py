from django.urls import path
from .feeds import LatestPostsFeed
from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.HomeListView.as_view(), name="home"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="detail"),
    path("posts/new/", views.PostCreateView.as_view(), name="create"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="edit"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="delete"),
    path("tags/<slug:slug>/", views.TagPostListView.as_view(), name="tag"),
    path("rss/", LatestPostsFeed(), name="rss"),
]
