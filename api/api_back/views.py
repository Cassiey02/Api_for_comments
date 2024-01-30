from typing import Any, Literal, Type

import rest_framework_simplejwt
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.db.models.manager import BaseManager
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from api_back.serializers import (TitleSerializer,
                                  GenreSerializer,
                                  CategorySerializer,
                                  CommentSerializer,
                                  ReviewSerializer,
                                  ReadOnlyTitleSerializer,
                                  UserSerializer,
                                  UserSignUpSerializer,
                                  UserTokenSerializer)
from api_back.mixins import (DeleteCreateListViewSet,
                             UpdateRetrieveViewSet)
from api_back.permissions import (AuthorOrReadOnly,
                                  IsAdminOrReadOnly,
                                  IsAdminOrSuperuser,
                                  IsAuthenticatedOrReadOnly)
from api_back.utils import create_confirmation_code
from api_back.filters import TitlesFilter
from reviews.models import Title, Genre, Category, Review
from users.models import User


class TitleViewSet(UpdateRetrieveViewSet, DeleteCreateListViewSet):
    """ViewSet модели Title."""

    queryset: BaseManager[Title] = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('id')
    permission_classes: tuple[type[IsAdminOrReadOnly]] = (IsAdminOrReadOnly, )
    http_method_names: tuple[str] = ('get', 'post', 'patch', 'delete')
    filter_backends: tuple[Type[DjangoFilterBackend]] = (DjangoFilterBackend,)
    filterset_class: type[TitlesFilter] = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class GenreViewSet(DeleteCreateListViewSet):
    """ViewSet модели Genre."""

    queryset: BaseManager[Genre] = Genre.objects.all()
    serializer_class: type[GenreSerializer] = GenreSerializer
    permission_classes: tuple[type[IsAdminOrReadOnly]] = (
        IsAdminOrReadOnly, )
    filter_backends: tuple[type[SearchFilter]] = (filters.SearchFilter,)
    search_fields: tuple[Literal['name']] = ('name',)
    lookup_field: str = "slug"


class CategoryViewSet(DeleteCreateListViewSet):
    """ViewSet модели Category."""

    queryset: BaseManager[Category] = Category.objects.all()
    serializer_class: type[CategorySerializer] = CategorySerializer
    permission_classes: tuple[type[IsAdminOrReadOnly]] = (
        IsAdminOrReadOnly, )
    pagination_class: type[PageNumberPagination] = PageNumberPagination
    filter_backends: tuple[type[SearchFilter]] = (filters.SearchFilter,)
    search_fields: tuple[Literal['name']] = ('name',)
    lookup_field: str = "slug"


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet модели Comment."""

    serializer_class: type[CommentSerializer] = CommentSerializer
    permission_classes: tuple = (AuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    http_method_names: tuple[str] = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        pk = self.kwargs.get('review_id')
        id = self.kwargs.get('title_id')
        title: Title = get_object_or_404(Title, id=id)
        review: Review = get_object_or_404(Review, pk=pk, title=title)
        queryset = review.comments.all()
        return queryset

    def perform_create(self, serializer):
        pk = self.kwargs.get('review_id')
        id = self.kwargs.get('title_id')
        title: Title = get_object_or_404(Title, id=id)
        review: Review = get_object_or_404(Review, pk=pk, title=title)
        serializer.save(author=self.request.user,
                        review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet модели Review."""

    serializer_class: type[ReviewSerializer] = ReviewSerializer
    permission_classes: tuple = (AuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    http_method_names: tuple[str] = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        pk = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=pk)
        queryset = title.reviews.all()
        return queryset

    def perform_create(self, serializer):
        pk = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=pk)
        serializer.save(author=self.request.user,
                        title=title)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet модели User."""

    queryset: Any = User.objects.all()
    permission_classes: tuple[type[IsAdminOrSuperuser]] = (IsAdminOrSuperuser,)
    serializer_class: type[UserSerializer] = UserSerializer
    filter_backends: tuple[type[SearchFilter]] = (SearchFilter,)
    search_fields: tuple[Literal['username']] = ('username',)

    @action(
        detail=False,
        methods=('get', 'patch', 'delete'),
        url_path=r'(?P<username>[\w.@+-]+)',
        url_name='get_user'
    )
    def get_user_by_username(self, request: Any, username: Any) -> Response:
        user: User = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer: type[UserSerializer] = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'DELETE':
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer: type[UserSerializer] = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get', 'patch'),
        url_path='me',
        url_name='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def about_me(self, request: Any) -> Response:
        if request.method == 'PATCH':
            serializer: type[UserSerializer] = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer: type[UserSerializer] = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserSignUpViewSet(APIView):
    """
    View для регистрации пользвателя получая
    код подтверждения на переданный email.
    """

    def post(self, request: Any) -> Response:
        email: str = request.data.get('email')
        username: str = request.data.get('username')
        serializer: type[UserSignUpSerializer] = UserSignUpSerializer(
            data=request.data
        )
        if User.objects.filter(username=username, email=email).exists():
            create_confirmation_code(username)
            return Response(
                {'email': serializer.initial_data['email'],
                 'username': serializer.initial_data['username']},
                status=status.HTTP_200_OK)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        confirmation_code: str = default_token_generator.make_token(user)
        send_mail(
            "Подтверждение регистрации на YaMDb!",
            "Для подтверждения регистрации отправьте код:"
            f"{confirmation_code}",
            "yamdb.host@yandex.ru",
            [user.email],
            False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTokenViewSet(APIView):
    """
    View для получение JWT-токена в обмен
    на username и confirmation code.
    """

    def post(self, request: Any) -> Response:
        serializer: type[UserTokenSerializer] = UserTokenSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        username: str = serializer.validated_data.get('username')
        user: User = get_object_or_404(User, username=username)
        refresh: rest_framework_simplejwt.tokens.RefreshToken = (
            RefreshToken.for_user(user))
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK
        )
