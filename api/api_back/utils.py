from typing import Any

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from users.models import User


def create_confirmation_code(username: Any) -> None:
    """Функция отправки сообщения."""
    user: User = get_object_or_404(User, username=username)
    confirmation_code: str = default_token_generator.make_token(user)
    send_mail(
        "Подтверждение регистрации на YaMDb!",
        "Для подтверждения регистрации отправьте код:"
        f"{confirmation_code}",
        "yamdb.host@yandex.ru",
        [user.email],
        False,
    )
