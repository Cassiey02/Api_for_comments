from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from .constants import COUNT_CHARACTERS, ONE_POINT, TEN_POINTS

User = get_user_model()


class Genre(models.Model):
    """Модель жанров"""

    name = models.CharField(
        verbose_name='Название',
        max_length=256)
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Уникальный адрес')

    def __str__(self):
        return self.name

    class Meta:
        """Модель Мета. Обозначены правила сортировки."""

        ordering: tuple[str] = ('name',)
        verbose_name: str = 'Жанр'
        verbose_name_plural: str = 'Жанры'


class Category(models.Model):
    """Модель категорий"""

    name = models.CharField(
        verbose_name='Название категории',
        max_length=256)
    slug = models.SlugField(max_length=50,
                            unique=True,
                            verbose_name='Уникальный адрес')

    def __str__(self):
        return self.name

    class Meta:
        """Модель Мета. Обозначены правила сортировки."""
        ordering: tuple[str] = ('name',)
        verbose_name: str = 'Категория'
        verbose_name_plural: str = 'Категории'


class Title(models.Model):
    """Модель произведений"""

    name = models.CharField(max_length=200,
                            verbose_name='Произведение')
    year = models.IntegerField(verbose_name='Год выпуска')
    description = models.TextField(
        verbose_name='Описание',
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория'
    )

    def __str__(self):
        return self.name[:COUNT_CHARACTERS]

    class Meta:
        """Модель Мета. Обозначены правила сортировки."""

        ordering: tuple[str] = ('year',)
        verbose_name: str = 'Произведение'
        verbose_name_plural: str = 'Произведения'


class GenreTitle(models.Model):
    """Модель жанров - произведений"""

    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        """Модель Мета. Задает имя в admin панели."""

        verbose_name: str = 'Жанр-произведение'
        verbose_name_plural: str = 'Жанры-произведения'


class Review(models.Model):
    """Модель отзывов"""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.CharField(
        max_length=256,
        verbose_name='Текст')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=ONE_POINT,
                message='не менее 1 балла'
            ),
            MaxValueValidator(
                limit_value=TEN_POINTS,
                message='не более 10 баллов'
            )
        ),
        verbose_name='Оценка'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        """
        Модель Мета. Обозначены правила сортировки.
        Обозначена уникальность полей.
        """

        unique_together: tuple[str] = ('title', 'author')
        ordering: tuple[str] = ('-pub_date',)
        verbose_name: str = 'Отзыв'
        verbose_name_plural: str = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментраиев"""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.CharField(
        max_length=256,
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    pub_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        """Модель Мета. Обозначены правила сортировки."""

        ordering: tuple[str] = ('-pub_date',)
        verbose_name: str = 'Комментарий'
        verbose_name_plural: str = 'Комментарии'

    def __str__(self):
        return self.text
