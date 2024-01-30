from datetime import date
from typing import Any

from django.contrib.auth.tokens import default_token_generator
from django.core import validators
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Title, Genre, Category, Comment, Review
from reviews.constants import ONE_POINT, TEN_POINTS
from users.models import User
from users.validators import ValidateUsername


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category"""

    class Meta:
        exclude: tuple[str] = ('id',)
        lookup_field: str = 'slug'
        extra_kwargs: dict = {
            'url': {'lookup_field': 'slug'}
        }
        model: type[Category] = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre"""

    class Meta:
        exclude: tuple[str] = ('id',)
        lookup_field: str = 'slug'
        extra_kwargs: dict = {
            'url': {'lookup_field': 'slug'}
        }
        model: type[Genre] = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title"""

    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model: type[Title] = Title
        fields: str = '__all__'

    def perform_create(self, serializer):
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def validate_year(self, value) -> int:
        """Проверка произведения на корректный год выпуска."""
        if value > date.today().year:
            raise serializers.ValidationError(
                'Произведение еще не вышло!'
            )
        return value

    def to_representation(self, instance):
        return ReadOnlyTitleSerializer(instance).data


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title(GET-запросы)"""

    rating = serializers.IntegerField(read_only=True, default=0)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model: type[Title] = Title
        fields: str = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment"""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields: str = (
            'id', 'text', 'author', 'pub_date')
        model: type[Comment] = Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review"""

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model: type[Review] = Review
        fields: str = (
            'id', 'text', 'author', 'score', 'pub_date')

    def validate_score(self, value: int) -> int:
        if ONE_POINT > value or TEN_POINTS < value:
            raise serializers.ValidationError(
                'Оценка должна быть не менее 1 и не больше 10'
            )
        return value

    def validate(self, data: dict) -> dict:
        """Запрещает пользователям оставлять повторные отзывы."""
        if not self.context.get('request').method == 'POST':
            return data
        author: User = self.context.get('request').user
        title_id: int = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение'
            )
        return data


class UserSerializer(ValidateUsername, serializers.ModelSerializer):
    """Сериализатор для модели User"""

    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=(
            validators.MaxLengthValidator(150),
            validators.RegexValidator(r'^[\w.@+-]+\Z')
        ),
    )
    email = serializers.EmailField(
        required=True,
        max_length=254,
        validators=(
            UniqueValidator(queryset=User.objects.all()),
        ),
    )

    class Meta:
        fields: tuple = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        model: type[User] = User

    def validate(self, attrs: Any) -> Any:
        """Проверка на зарегистрированную почту и имя пользователя"""
        if User.objects.filter(email=attrs.get('email')).exists():
            user: User = User.objects.get(email=attrs.get('email'))
            if user.username != attrs.get('username'):
                raise serializers.ValidationError(
                    {
                        "Ошибка": "Электронная почта уже используется!"
                    }
                )
        if User.objects.filter(username=attrs.get('username')).exists():
            user: User = User.objects.get(username=attrs.get('username'))
            if user.email != attrs.get('email'):
                raise serializers.ValidationError(
                    {
                        "Ошибка": "Имя пользователя уже использовано!"
                    }
                )
        return super().validate(attrs)


class UserSignUpSerializer(ValidateUsername, serializers.ModelSerializer):
    """Сериализатор для регистрации модели User"""

    class Meta:
        model: type[User] = User
        fields: tuple[str, str] = ('email', 'username')


class UserTokenSerializer(serializers.Serializer):
    """Сериализотор для получения токена пользователем"""

    token = serializers.CharField(max_length=255, read_only=True)
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields: tuple[str, str] = ('username', 'confirmation_code',)

    def validate(self, data: dict) -> dict:
        """Проверка наличия кода подтверждения"""
        user: User = get_object_or_404(User, username=data['username'])
        token = data['confirmation_code']
        confirmation_code: bool = default_token_generator.check_token(
            user, token)
        if not confirmation_code:
            raise serializers.ValidationError(
                {'Код подтверждения отсутствует'}
            )
        return data
