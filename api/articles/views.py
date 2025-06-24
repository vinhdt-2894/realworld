from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from api.articles.models import Article, Comment
from api.articles.serializers import ArticleSerializer, CommentSerializer
from rest_framework import status
from rest_framework.views import APIView

class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.select_related('author').prefetch_related('tags').order_by('-created_at')
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__username', 'tags__name']
    search_fields = ['title', 'body', 'description']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        tag = self.request.query_params.get('tag')
        author = self.request.query_params.get('author')
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
            return self.get_paginated_response({
                "articles": serializer.data,
                "articlesCount": queryset.count()
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "articles": serializer.data,
            "articlesCount": queryset.count()
        })

class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.select_related('author').prefetch_related('tags')
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        article = self.get_object()
        serializer = self.get_serializer(article)
        return Response({"article": serializer.data})


class ArticleCommentsListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        article = generics.get_object_or_404(Article, slug=slug)
        return Comment.objects.filter(article=article).order_by("-created_at")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"comments": serializer.data})

    def perform_create(self, serializer):
        slug = self.kwargs.get("slug")
        article = generics.get_object_or_404(Article, slug=slug)
        # TODO update this to use the authenticated user
        from api.users.models import CustomUser
        author = CustomUser.objects.get(pk=1)
        serializer.save(article=article, author=author)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"comment": serializer.data}, status=status.HTTP_201_CREATED)

class ArticleFeedView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Article.objects.filter(author=user).order_by('-created_at')

class ArticleFavoriteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        article = generics.get_object_or_404(Article, slug=slug)
        article.favorited_by.add(request.user)
        article.save()
        serializer = ArticleSerializer(article)
        return Response({"article": serializer.data})

    def delete(self, request, slug):
        article = generics.get_object_or_404(Article, slug=slug)
        article.favorited_by.remove(request.user)
        article.save()
        serializer = ArticleSerializer(article)
        return Response({"article": serializer.data})
