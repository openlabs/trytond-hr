# -*- coding: utf-8 -*-
"""
    Payroll

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from dateutil.relativedelta import relativedelta
from trytond.model import ModelView, ModelSQL, fields
from trytond.tools import datetime_strftime
from trytond.pyson import Eval, If
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['PayrollYear', 'PayrollPeriod', 'PayrollHoliday']


STATES = {
    'readonly': Eval('state') == 'close',
}
DEPENDS = ['state']


class PayrollYear(ModelSQL, ModelView):
    'Payroll Year'
    __name__ = 'payroll.year'

    name = fields.Char('Name', required=True, depends=DEPENDS)
    start_date = fields.Date('Start Date', required=True,
        states=STATES, depends=DEPENDS)
    end_date = fields.Date('End Date', required=True,
        states=STATES, depends=DEPENDS)
    periods = fields.One2Many(
        'payroll.period', 'payroll_year', 'Periods',
        states=STATES, depends=DEPENDS
    )
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close')
    ], 'State', readonly=True, select=True, required=True)
    company = fields.Many2One('company.company', 'Company', required=True,
        domain=[
            ('id', If(Eval('context', {}).contains('company'), '=', '!='),
                Eval('context', {}).get('company', 0)),
            ], select=True, states=STATES, depends=DEPENDS
        )
    department = fields.Many2One(
        'company.department', 'Department', required=True, select=True,
        domain=[('company', '=', Eval('company'))],
        states=STATES, depends=DEPENDS
    )

    @staticmethod
    def default_state():
        return 'open'

    @staticmethod
    def default_company():
        return Transaction().context.get('company')

    @classmethod
    def __setup__(cls):
        super(PayrollYear, cls).__setup__()
        cls._constraints += [
            ('check_dates', 'payrollyear_overlaps'),
        ]
        cls._order.insert(0, ('start_date', 'ASC'))
        cls._error_messages.update({
            'payrollyear_overlaps': \
                'You can not have 2 payroll years that overlap!',
        })
        cls._buttons.update({
            'create_period': {
                'invisible': ((Eval('state') != 'open')
                    | Eval('periods', [0])),
            },
            'close': {
                'invisible': Eval('state') != 'open',
            },
            'reopen': {
                'invisible': Eval('state') != 'close',
            },
        })

    @classmethod
    @ModelView.button
    def close(cls, payrollyears):
        '''
        Close a payroll year
        '''
        Period = Pool().get('payroll.period')
        cls.write(payrollyears, {'state': 'close'})
        for payrollyear in payrollyears:
            Period.write(payrollyear.periods, {'state': 'close'})

    @classmethod
    @ModelView.button
    def reopen(cls, payrollyears):
        '''
        Reopen a payroll year
        '''
        cls.write(payrollyears, {'state': 'open'})

    def check_dates(self):
        cursor = Transaction().cursor
        cursor.execute('SELECT id ' \
            'FROM ' + self._table + ' ' \
            'WHERE ((start_date <= %s AND end_date >= %s) ' \
                    'OR (start_date <= %s AND end_date >= %s) ' \
                    'OR (start_date >= %s AND end_date <= %s)) ' \
                'AND company = %s ' \
                'AND id != %s',
            (self.start_date, self.start_date,
                self.end_date, self.end_date,
                self.start_date, self.end_date,
                self.company.id, self.id))
        if cursor.fetchone():
            return False
        return True

    @classmethod
    @ModelView.button
    def create_period(cls, payrollyears, interval=1):
        '''
        Create periods for the payroll years with month interval
        '''
        Period = Pool().get('payroll.period')
        for payrollyear in payrollyears:
            period_start_date = payrollyear.start_date
            while period_start_date < payrollyear.end_date:
                period_end_date = period_start_date + \
                        relativedelta(months=interval - 1) + \
                        relativedelta(day=31)
                if period_end_date > payrollyear.end_date:
                    period_end_date = payrollyear.end_date
                name = datetime_strftime(period_start_date, '%Y-%m')
                if name != datetime_strftime(period_end_date, '%Y-%m'):
                    name += ' - ' + datetime_strftime(period_end_date, '%Y-%m')
                Period.create({
                    'name': name,
                    'start_date': period_start_date,
                    'department': payrollyear.department.id,
                    'end_date': period_end_date,
                    'payroll_year': payrollyear.id,
                    })
                period_start_date = period_end_date + relativedelta(days=1)


class PayrollPeriod(ModelSQL, ModelView):
    'Payroll Period'
    __name__ = 'payroll.period'

    name = fields.Char('Name', required=True, select=True, depends=DEPENDS)
    payroll_year = fields.Many2One('payroll.year', 'Year', required=True,
        states=STATES, depends=DEPENDS
    )
    department = fields.Many2One(
        'company.department', 'Department', required=True, select=True,
        states=STATES, depends=DEPENDS
    )
    start_date = fields.Date('Start Date', required=True,
        states=STATES, depends=DEPENDS
    )
    end_date = fields.Date('End Date', required=True,
        states=STATES, depends=DEPENDS
    )
    holidays = fields.One2Many(
        'payroll.holiday', 'period', 'Holidays', states=STATES, depends=DEPENDS
    )
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close')
    ], 'State', readonly=True, select=True, required=True)

    @staticmethod
    def default_state():
        return 'open'

    @classmethod
    def __setup__(cls):
        super(PayrollPeriod, cls).__setup__()
        cls._constraints += [
            ('check_dates', 'periods_overlaps'),
        ]
        cls._order.insert(0, ('start_date', 'ASC'))
        cls._error_messages.update({
            'periods_overlaps': 'You can not have two overlapping periods!',
        })
        cls._buttons.update({
            'close': {
                'invisible': Eval('state') != 'open',
            },
            'reopen': {
                'invisible': Eval('state') != 'close',
            },
        })

    @classmethod
    @ModelView.button
    def close(cls, periods):
        '''
        Close a payroll year
        '''
        cls.write(periods, {'state': 'close'})

    @classmethod
    @ModelView.button
    def reopen(cls, periods):
        '''
        Reopen a payroll year
        '''
        PayrollYear = Pool().get('payroll.year')
        cls.write(periods, {'state': 'open'})
        for period in periods:
            PayrollYear.write([period.payroll_year], {'state': 'open'})


    def check_dates(self):
        cursor = Transaction().cursor
        cursor.execute('SELECT id ' \
            'FROM "' + self._table + '" ' \
            'WHERE ((start_date <= %s AND end_date >= %s) ' \
                    'OR (start_date <= %s AND end_date >= %s) ' \
                    'OR (start_date >= %s AND end_date <= %s)) ' \
                'AND payroll_year = %s ' \
                'AND id != %s',
            (self.start_date, self.start_date,
                self.end_date, self.end_date,
                self.start_date, self.end_date,
                self.payroll_year.id, self.id))
        return not cursor.fetchone()


class PayrollHoliday(ModelSQL, ModelView):
    'Payroll Holiday'
    __name__ = 'payroll.holiday'

    period = fields.Many2One(
        'payroll.period', 'Payroll Period', required=True
    )
    date = fields.Date('Date', required=True, select=True, depends=['period'])

    @classmethod
    def __setup__(cls):
        super(PayrollHoliday, cls).__setup__()
        cls._constraints += [
            ('check_date', 'wrong_date'),
        ]
        cls._error_messages.update({
             'wrong_date': \
                'The date must be between start and end date of period',
        })

    def check_date(self):
        'Check if the date is between start and end date of period'
        if self.date < self.period.start_date or \
                self.date > self.period.end_date:
            return False
        return True
