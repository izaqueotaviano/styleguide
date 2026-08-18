"""Usuário customizado do projeto.

Definimos um ``User`` próprio desde o início (recomendação oficial do
Django): trocar depois do primeiro migrate é extremamente doloroso.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField("e-mail", unique=True)

    def __str__(self) -> str:
        return self.username
