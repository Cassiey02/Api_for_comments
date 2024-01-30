from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'reviews'
    verbose_name: str = 'Отзывы'
