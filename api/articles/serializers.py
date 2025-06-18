from rest_framework import serializers
from api.articles.models import Article, Comment
from api.users.models import CustomUser
class ArticleSerializer(serializers.ModelSerializer):
    author = CustomUser()
    tagList = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['slug', 'title', 'description', 'body', 'created_at', 'updated_at', 'tagList', 'author']

    def get_tagList(self, obj):
        return [tag.name for tag in obj.tags.all()]

# Comment Serializer
class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "body", "created_at", "updated_at", "author"]
