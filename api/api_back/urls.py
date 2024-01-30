from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (TitleViewSet, CategoryViewSet, GenreViewSet,
                    ReviewViewSet, CommentViewSet, UserViewSet,
                    UserSignUpViewSet, UserTokenViewSet)

app_name = 'api'

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='users')
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewSet, basename='categories')
router.register('genres', GenreViewSet, basename='genres')
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path(
        'v1/auth/signup/',
        UserSignUpViewSet.as_view(),
        name='user_signup'
    ),
    path(
        'v1/auth/token/',
        UserTokenViewSet.as_view(),
        name='token'
    ),
    path(
        'v1/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),
    path('v1/', include(router.urls))
]
