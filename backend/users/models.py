from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


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
        verbose_name=_('username')
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=False
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=False
    )
    password = models.CharField(
        verbose_name=_('password'),
        max_length=150
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
    is_subscribed = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        related_name='is_subscribed'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_subscribed'],
                name='subscribe_constraints'
            )
        ]

    def __str__(self):
        return '{user} is subscribed to {is_subscribed}'.format(
            user=self.user,
            is_subscribed=self.is_subscribed
        )
