# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal

import requests

from trytond.config import config
from trytond.modules.currency.currency import CronFetchError
from trytond.pool import PoolMeta
from trytond.pyson import Eval, If
import logging

logger = logging.getLogger(__name__)

URL = 'https://dolarapi.com/v1/dolares/oficial'
TIMEOUT = config.getfloat('currency_ar', 'requests_timeout', default=300)


class Cron(metaclass=PoolMeta):
    __name__ = 'currency.cron'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.source.selection.append(('bna_ar', "Argentinian National Bank"))
        cls.currency.domain = [
            cls.currency.domain or [],
            If(Eval('source') == 'bna_ar',
                ('code', 'in', ['ARS', 'USD']),
                ()),
            ]

    def fetch_bna_ar(self, date):
        try:
            response = requests.get(URL, timeout=TIMEOUT)
        except requests.HTTPError as e:
            raise CronFetchError() from e

        data = response.json()
        logger.info('fetch_bna_ar response %s', data)
        if data and 'venta' in data:
            rate = data['venta']
            logger.info('fetch_bna_ar rates %s', rate)
            return {
                'USD': (Decimal('1.0') / Decimal(rate)),
                'ARS': (Decimal(rate))
                }
        else:
            return {}
