from django.db import models
from django.contrib.auth.models import AbstractUser

from users.validators import username_regular


class User(AbstractUser):
    """Кастомная модель User"""

    USER: str = "user"
    MODERATOR: str = "moderator"
    ADMIN: str = "admin"

    ROLE_CHOICES: tuple = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    username = models.CharField(
        verbose_name='Никнейм пользователя',
        unique=True,
        blank=False,
        null=False,
        validators=[username_regular],
        help_text="Введите имя пользователя",
        max_length=150
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=254
    )
    first_name = models.CharField(
        verbose_name='Имя',
        blank=True,
        max_length=150
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=True,
        max_length=150
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
        help_text='Здесь напишите о себе'
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        choices=ROLE_CHOICES,
        default=USER,
        max_length=30,
        blank=True,
        help_text='Выберите роль пользователя',
    )

    class Meta:
        verbose_name: str = 'Пользователь'
        verbose_name_plural: str = 'Пользователи'
        ordering: tuple[str] = ('username',)
        constraints: list = (
            models.UniqueConstraint(
                fields=('username', 'email'),
                name='unique_user'
            ),
        )

    def __str__(self):
        return self.username

    @property
    def is_moderator(self) -> bool:
        """Проверка пользователя на наличие прав модератора."""
        return self.role in (self.MODERATOR, self.ADMIN, self.is_superuser)

    @property
    def is_admin(self) -> bool:
        """Проверка пользователя на наличие прав администратора."""
        return self.role in (self.ADMIN, self.is_superuser)

    @property
    def is_user(self) -> bool:
        return self.role == self.USER
