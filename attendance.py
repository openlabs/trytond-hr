# -*- coding: utf-8 -*-
"""
    Attendance

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, Workflow, fields
from trytond.pool import Pool
from trytond.pyson import Eval

__all__ = [
    'Attendance', 'AttendanceSummary', 'LeaveApplication',
]


class Attendance(ModelSQL, ModelView):
    'Attendance'
    __name__ = 'employee.attendance'

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True, select=True
    )
    date = fields.Date('Date', required=True, select=True)
    period = fields.Function(
        fields.Many2One('payroll.period', 'Period', depends=['date']),
        'get_period'
    )
    is_holiday = fields.Function(
        fields.Boolean('Is a Holiday ?', depends=['date']),
        'get_is_holiday',
    )

    # Make these fields as Time fields which seems to be broken somehow
    in_time = fields.DateTime('In time')
    out_time = fields.DateTime('Out time')

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()

    @classmethod
    def __setup__(cls):
        super(Attendance, cls).__setup__()
        cls._constraints += [
            ('check_in_time', 'missing_in_time'),
            ('check_times', 'wrong_times'),
            ('check_out_time', 'invalid_out_time'),
        ]
        cls._error_messages.update({
            'invalid_period': 'Either 0 or more than 1 periods found for '
                'this date! There should be only 1 period for this date',
             'wrong_times': 'The day on In time and Out time should be same',
             'missing_in_time': \
                'Out time can only be entered if In time is provided',
            'invalid_out_time': 'Out time cannot be lesser than In time',
        })

    def check_in_time(self):
        'Check if In time is provided before Out time'
        if self.out_time and not self.in_time:
            return False
        return True

    def check_times(self):
        'Check if the In time and Out time are on same day'
        if self.in_time and self.out_time and \
                not self.in_time.date() == self.out_time.date():
            return False
        return True

    def check_out_time(self):
        'Check if Out time is not lesser than In time'
        if self.in_time and self.out_time and self.out_time <= self.in_time:
            return False
        return True

    def get_period(self, name):
        Period = Pool().get('payroll.period')

        periods = Period.search([
            ('state', '=', 'open'),
            ('start_date', '<=', self.date),
            ('end_date', '>=', self.date),
        ])
        if not periods or len(periods) > 1:
            self.raise_user_error('invalid_period')

        return periods[0].id

    def get_is_holiday(self, name):
        if not self.period:
            return False
        holidays = [holiday.date for holiday in self.period.holidays]
        if self.in_time.date() in holidays:
            return True
        return False


class AttendanceSummary(ModelSQL, ModelView):
    'Attendance Summary'
    __name__ = 'employee.attendance.summary'

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True, select=True
    )
    period = fields.Function(
        fields.Many2One('payroll.period', 'Period'), 'get_period'
    )
    full_days = fields.Integer('Full Days')
    half_days = fields.Integer('Half Days')
    leaves = fields.Numeric('Leaves Taken')


class LeaveApplication(Workflow, ModelSQL, ModelView):
    "Leave Application"
    __name__ = 'employee.leave.application'

    from_date = fields.Date('From Date', required=True, select=True,
        states={'readonly': Eval('state') != 'Draft'}, depends=['state']
    )
    to_date = fields.Date('To Date', required=True, select=True,
        states={'readonly': Eval('state') != 'Draft'}, depends=['state']
    )
    employee = fields.Many2One(
        'company.employee', 'Employee', required=True, select=True,
        states={'readonly': Eval('state') != 'Draft'}, depends=['state']
    )
    reason = fields.Text('Reason',
        states={'readonly': Eval('state') != 'Draft'}, depends=['state']
    )
    type = fields.Selection([
        ('full_day', 'Full Day'),
        ('first_half', 'First Half'),
        ('second_half', 'Second Half')
    ], 'Type', required=True,
        states={'readonly': Eval('state') != 'Draft'}, depends=['state']
    )
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('In Review', 'In Review'),
        ('Approved', 'Approved'),
        ('Denied', 'Denied')
    ], 'State', readonly=True, required=True)

    @staticmethod
    def default_state():
        return 'Draft'

    @staticmethod
    def default_type():
        return 'full_day'

    @classmethod
    def __setup__(cls):
        super(LeaveApplication, cls).__setup__()
        cls._order.insert(0, ('from_date', 'DESC'))
        cls._transitions |= set((
            ('Draft', 'In Review'),
            ('In Review', 'Approved'),
            ('In Review', 'Denied'),
        ))
        cls._buttons.update({
            'review': {
                'invisible': Eval('state') != 'Draft',
            },
            'approve': {
                'invisible': Eval('state') != 'In Review',
            },
            'deny': {
                'invisible': Eval('state') != 'In Review',
            }
        })
        cls._constraints += [
            ('check_type', 'wrong_type'),
        ]
        cls._error_messages.update({
            'wrong_type': \
                'Type cannot be half day if from and to dates are not same'
        })

    def check_type(self):
        'Type cannot be half day if from and to dates are not same'
        if self.from_date != self.to_date and self.type != 'full_day':
            return False
        return True

    @classmethod
    @ModelView.button
    @Workflow.transition('In Review')
    def review(cls, apps):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('Approved')
    def approve(cls, apps):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('Denied')
    def deny(cls, apps):
        pass
