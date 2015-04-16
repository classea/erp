# -*- coding: utf-8 -*-
from decimal import Decimal

from django.utils import timezone
import pytz


def valor(moeda):
    return u"R$ {}".format(moeda.quantize(Decimal("0.00"), 2)).replace('.', ',')


def hoje():
    return timezone.now().date()


def agora():
    return timezone.now()


local_timezone = pytz.timezone("America/Sao_Paulo")

MESES = ((1, u"Janeiro"),
         (2, u"Fevereiro"),
         (3, u"Março"),
         (4, u"Abril"),
         (5, u"Maio"),
         (6, u"Junho"),
         (7, u"Julho"),
         (8, u"Agosto"),
         (9, u"Setembro"),
         (10, u"Outubro"),
         (11, u"Novembro"),
         (12, u"Dezembro"))

DIAS_SEMANA = ((0, u"Segunda"),
               (1, u"Terça"),
               (2, u"Quarta"),
               (3, u"Quinta"),
               (6, u"Sexta"),
               (7, u"Sábado"),
               (8, u"Domingo"))

TIPO_RECORRENCIA = ((0, u"Diariamente"),
                    (1, u"Semanalmente"),
                    (2, u"Mensalmente"),
                    (3, u"Anualmente"),
                    (4, u"Dia do Mês"),
                    (5, u"Dia do Ano"),
                    )


def teste_operador(usuario):
    try:
        return True if usuario.empresa_operador_caixa else False
    except AttributeError:
        return False