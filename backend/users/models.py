from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=150,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        null=True
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=200,
        unique=True,
        db_index=True,
        null=False,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return (
            f'Пользователь {self.first_name} {self.last_name} '
            f'({self.username})'
        )
