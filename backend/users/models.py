from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscription',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'], name='unique_subscriptions'
            )
        ]
        unique_together = ['author', 'subscriber']

    def __str__(self):
        return (
            f'Пользователь {self.subscriber.username} - '
            f'подписчик автора: {self.author.username}'
        )
