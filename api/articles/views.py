from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from api.articles.models import Article, Comment
from api.articles.serializers import ArticleSerializer, CommentSerializer
from rest_framework import status
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from django.core.exceptions import PermissionDenied


@extend_schema(tags=["Articles"])
class ArticleListView(generics.ListCreateAPIView):
    queryset = (
        Article.objects.select_related("author")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    serializer_class = ArticleSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["author__username", "tags__name"]
    search_fields = ["title", "body", "description"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get("tag")
        author = self.request.query_params.get("author")
        if tag:
            queryset = queryset.filter(tags__name=tag)
        if author:
            queryset = queryset.filter(author__username=author)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                {"articles": serializer.data, "articlesCount": queryset.count()}
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"articles": serializer.data, "articlesCount": queryset.count()}
        )


@extend_schema(tags=["Articles"])
class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.select_related("author").prefetch_related("tags")
    serializer_class = ArticleSerializer
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = self.get_serializer(article)
        return Response({"article": serializer.data})


@extend_schema(tags=["Articles"])
class ArticleCommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        article = generics.get_object_or_404(Article, slug=slug)
        return Comment.objects.filter(article=article).order_by("-created_at")

    def perform_create(self, serializer):
        slug = self.kwargs.get("slug")
        article = generics.get_object_or_404(Article, slug=slug)
        serializer.save(article=article, author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"comment": serializer.data}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Articles"])
class ArticleFeedView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = user.following.all()
        return Article.objects.filter(author__in=following_users).order_by(
            "-created_at"
        )


@extend_schema(tags=["Articles"])
class ArticleFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, *args, **kwargs):
        article = generics.get_object_or_404(Article, slug=slug)
        article.favorited_by.add(request.user)
        article.save()
        serializer = ArticleSerializer(article)
        return Response({"article": serializer.data})

    def delete(self, request, slug, *args, **kwargs):
        article = generics.get_object_or_404(Article, slug=slug)
        article.favorited_by.remove(request.user)
        article.save()
        serializer = ArticleSerializer(article)
        return Response({"article": serializer.data})


@extend_schema(tags=["Articles"])
class ArticleCommentDeleteView(generics.DestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        article = generics.get_object_or_404(Article, slug=slug)
        return Comment.objects.filter(article=article)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied("You do not have permission to delete this comment.")
        instance.delete()
