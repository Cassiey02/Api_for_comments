from typing import NoReturn, Union

from csv import DictReader
from django.core.management import BaseCommand

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title, User)


file_category: str = './static/data/category.csv'
file_genre: str = './static/data/genre.csv'
file_users: str = './static/data/users.csv'
file_titles: str = './static/data/titles.csv'
file_reviews: str = './static/data/review.csv'
file_comments: str = './static/data/comments.csv'
file_genre_title: str = './static/data/genre_title.csv'

FILES_MODELS: dict = {
    file_category: Category,
    file_genre: Genre,
    file_users: User,
    file_titles: Title,
    file_reviews: Review,
    file_comments: Comment,
    file_genre_title: GenreTitle,
}


def verify_value(key: str, value: int,
                 model) -> Union[Category, Title, int]:
    """Функция для сопоставления модели и значений."""
    if model == Title and key == 'category':
        return Category.objects.get(id=int(value))
    elif model == Review and key == 'title':
        return Title.objects.get(id=int(value))
    elif key == 'author':
        return User.objects.get(id=int(value))
    elif 'id' in key:
        return int(value)
    else:
        return value


class Command(BaseCommand):
    """Класс для загрузки данных из CSV файла."""

    help: str = "Loads data from data folder"

    def handle(self, *args, **options) -> NoReturn:
        if not load():
            print('Please, verify console logs')
        else:
            print('Congratulate you, DATA UPLOADED')


def load() -> bool:
    """Функция загрузки данных из CSV файла."""
    for file, model in FILES_MODELS.items():
        reader: DictReader = DictReader(open(file, encoding='utf8'))
        obj: list = []
        for row in reader:
            for key, value in row.items():
                row[key] = verify_value(key, value, model)
            obj.append(model(**row))
        model.objects.bulk_create(obj)
    return True
