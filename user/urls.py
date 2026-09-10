from django.urls import path

from .views import (
    NewsListView,
    RecentNewsView,
    NewsDetailView,
    NewsViewCountView,
    NewsByDateView,
    NewsCategoriesView,
)

urlpatterns = [
    path("", NewsListView.as_view(), name="news-list"),
    path("recent/", RecentNewsView.as_view(), name="recent-news"),
    path("categories/", NewsCategoriesView.as_view(), name="news-categories"),
    path("by-date/", NewsByDateView.as_view(), name="news-by-date"),
    path("<slug:slug>/", NewsDetailView.as_view(), name="news-detail"),
    path("<slug:slug>/view/", NewsViewCountView.as_view(), name="news-view-count"),
]