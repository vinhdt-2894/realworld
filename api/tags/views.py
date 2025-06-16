from rest_framework import viewsets
from rest_framework.response import Response
from .models import Tag
from .serializers import TagSerializer

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def list(self, request, *args, **kwargs):
        tag_names = [tag.name for tag in self.get_queryset()]
        return Response({"tags": tag_names})
