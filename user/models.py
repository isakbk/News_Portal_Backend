from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User


class News(models.Model):
    CATEGORY_CHOICES = [
        ("National", "National"),
        ("International", "International"),
        ("Technology", "Technology"),
        ("Sports", "Sports"),
        ("Business", "Business"),
        ("Entertainment", "Entertainment"),
        ("Health", "Health"),
        ("Education", "Education"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)

    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="National"
    )

    summary = models.TextField(
        max_length=500,
        help_text="Short description shown on the homepage."
    )

    content = models.TextField(
        help_text="Rich HTML content from TinyMCE."
    )

    image = models.ImageField(
        upload_to="news/images/",
        blank=True,
        null=True
    )

    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="published_news"
    )

    published_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_published = models.BooleanField(default=True)

    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title