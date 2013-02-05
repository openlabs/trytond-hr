# -*- coding: utf-8 -*-
"""
    Payroll

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields

__all__ = ['PayrollPeriod', 'PayrollHoliday']


class PayrollPeriod(ModelSQL, ModelView):
    'Payroll Period'
    __name__ = 'payroll.period'

    name = fields.Char('Name', required=True, select=True)
    department = fields.Many2One(
        'company.department', 'Department', required=True, select=True
    )
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    holidays = fields.One2Many(
        'payroll.holiday', 'period', 'Holidays'
    )
    state = fields.Selection([
        ('open', 'Open'),
        ('close', 'Close')
    ], 'State', readonly=True, select=True, required=True)

    @staticmethod
    def default_state():
        return 'open'

    @staticmethod
    def create_monthly_periods():
        "Create monthly periods automatically"
        #TODO
        pass

    def close_period(self):
        """This method will close this attendance period
        if the end_date has passed. This will create records in
            employee.attendance.summary per employee.
        """
        #TODO
        pass


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
