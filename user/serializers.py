from rest_framework import serializers
from .models import News


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = News
        fields = [
            "id",
            "title",
            "slug",
            "category",
            "summary",
            "content",
            "image",
            "image_url",
            "author",
            "author_name",
            "published_at",
            "updated_at",
            "is_published",
            "view_count",
        ]

        read_only_fields = [
            "id",
            "slug",
            "author",
            "published_at",
            "updated_at",
            "view_count",
        ]

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.username
        return "Unknown"

    def get_image_url(self, obj):
        request = self.context.get("request")

        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url

        return None