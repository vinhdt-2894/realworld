from rest_framework import generics
from rest_framework.response import Response
from api.articles.models import Article, Comment
from api.articles.serializers import ArticleSerializer, CommentSerializer
from rest_framework import status

class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.select_related('author').prefetch_related('tags').order_by('-created_at')
    serializer_class = ArticleSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
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
