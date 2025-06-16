from rest_framework import generics
from rest_framework.response import Response
from api.articles.models import Article
from api.articles.serializers import ArticleSerializer

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
