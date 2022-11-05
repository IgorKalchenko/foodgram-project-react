from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager
from api.validators import OnlyLettersValidator


class CustomUser(AbstractUser):
    objects = CustomUserManager()
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        verbose_name=_('username')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=False,
        validators=[OnlyLettersValidator]
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=False,
        validators=[OnlyLettersValidator]
    )
    password = models.CharField(
        verbose_name=_('password'),
        max_length=150,
        blank=False
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}'


class Subscription(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='subscribe_constraints'
            )
        ]

    def __str__(self):
        return '{user} is subscribed to {author}'.format(
            user=self.user,
            author=self.author
        )
