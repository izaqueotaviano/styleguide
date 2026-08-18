"""Tradução de exceções de domínio para respostas HTTP da API.

A camada de services levanta ``django.core.exceptions.ValidationError``
(sem depender do DRF). Aqui convertemos para ``ValidationError`` do DRF,
para que o cliente receba um 400 bem formatado em vez de um 500.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as base_exception_handler


def drf_exception_handler(exc: Exception, context: dict) -> Response | None:
    if isinstance(exc, DjangoValidationError):
        detail = getattr(exc, "message_dict", None) or exc.messages
        exc = drf_exceptions.ValidationError(detail)
    return base_exception_handler(exc, context)
