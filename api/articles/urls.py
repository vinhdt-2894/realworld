from django.urls import path
from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleCommentsListCreateView,
    ArticleFeedView,
    ArticleFavoriteView,
)

urlpatterns = [
    path("", ArticleListView.as_view(), name="articles-list"),
    path("feed/", ArticleFeedView.as_view(), name="articles-feed"),
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
    path(
        "<slug:slug>/comments/",
        ArticleCommentsListCreateView.as_view(),
        name="article-comments",
    ),
    path(
        "<slug:slug>/favorite/", ArticleFavoriteView.as_view(), name="article-favorite"
    ),
]
