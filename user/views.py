from datetime import timedelta

from django.db.models import F, Q
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import News
from .serializers import NewsSerializer


class NewsListView(generics.ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = News.objects.filter(is_published=True)

        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")

        if category:
            queryset = queryset.filter(category=category)

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(summary__icontains=search)
                | Q(content__icontains=search)
            )

        return queryset


class RecentNewsView(generics.ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        five_days_ago = timezone.now() - timedelta(days=5)

        return News.objects.filter(
            is_published=True,
            published_at__gte=five_days_ago
        )


class NewsDetailView(generics.RetrieveAPIView):
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return News.objects.filter(is_published=True)


class NewsViewCountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        try:
            news = News.objects.get(
                slug=slug,
                is_published=True
            )
        except News.DoesNotExist:
            return Response(
                {"detail": "News not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        News.objects.filter(pk=news.pk).update(
            view_count=F("view_count") + 1
        )

        news.refresh_from_db()

        return Response({
            "message": "View counted successfully.",
            "view_count": news.view_count
        })


class NewsByDateView(generics.ListAPIView):
    serializer_class = NewsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        date = self.request.query_params.get("date")

        queryset = News.objects.filter(is_published=True)

        if date:
            queryset = queryset.filter(published_at__date=date)

        return queryset


class NewsCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        categories = [
            {"value": value, "label": label}
            for value, label in News.CATEGORY_CHOICES
        ]

        return Response(categories)