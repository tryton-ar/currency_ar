====================
Currency AR Scenario
====================

Imports::

    >>> import datetime as dt
    >>> import os
    >>> from proteus import Model
    >>> from trytond.tests.tools import activate_modules
    >>> today = dt.date.today()
    >>> previous_month = today - dt.timedelta(days=30)
    >>> before_previous_month = previous_month - dt.timedelta(days=1)

Activate modules::

    >>> config = activate_modules('currency_ar')

Create some currencies::

    >>> Currency = Model.get('currency.currency')
    >>> usd = Currency(name="USD", code='USD', symbol="U$")
    >>> usd.save()
    >>> ars = Currency(name="Peso Argentino", code='ARS', symbol="$")
    >>> ars.save()

Setup cron::

    >>> Cron = Model.get('currency.cron')
    >>> cron = Cron()
    >>> cron.source = 'bna_ar'
    >>> cron.frequency = 'daily'
    >>> cron.day = None
    >>> cron.currency = usd
    >>> cron.currencies.append(Currency(ars.id))
    >>> cron.last_update = before_previous_month
    >>> cron.save()

Run update::

    >>> cron.click('run')
    >>> cron.last_update >= previous_month
    True

    >>> ars.reload()
    >>> rate = [r for r in ars.rates if r.date < today][0]
    >>> bool(rate.rate)
    True
    >>> usd.reload()
    >>> rate = [r for r in usd.rates if r.date < today][0]
    >>> rate.rate
    Decimal('1.000000')
