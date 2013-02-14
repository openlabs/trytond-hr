# -*- coding: utf-8 -*-
"""
    configuration

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields

__all__ = ['Configuration', 'LeaveConfiguration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Employee Configuration'
    __name__ = 'company.employee.configuration'

    employee_sequence = fields.Property(fields.Many2One(
            'ir.sequence', 'Employee Sequence',
            domain=[('employee_id', '=', 'company.employee')]
    ))


class LeaveConfiguration(ModelSingleton, ModelSQL, ModelView):
    "Leave Configuration"
    __name__ = 'employee.leave.configuration'

    probation_cl = fields.Integer('Probation Casual Leaves')
    probation_sl = fields.Integer('Probation Sick Leaves')
    probation_el = fields.Integer('Probation Earned Leaves')
    confirmed_cl = fields.Integer('Confirmed Casual Leaves')
    confirmed_sl = fields.Integer('Confirmed Sick Leaves')
    confirmed_el = fields.Integer('Confirmed Earned Leaves')

    probation_dl = fields.Integer('Probation Study Leaves')
    probation_pl = fields.Integer('Probation Paternity Leaves')
    probation_al = fields.Integer('Probation Annual Leaves')
    confirmed_dl = fields.Integer('Confirmed Study Leaves')
    confirmed_pl = fields.Integer('Confirmed Paternity Leaves')
    confirmed_al = fields.Integer('Confirmed Annual Leaves')

    @staticmethod
    def default_probation_cl():
        return 5

    @staticmethod
    def default_probation_sl():
        return 5

    @staticmethod
    def default_probation_el():
        return 0

    @staticmethod
    def default_confirmed_cl():
        return 10

    @staticmethod
    def default_confirmed_sl():
        return 10

    @staticmethod
    def default_confirmed_el():
        return 15

    @staticmethod
    def default_probation_dl():
        return 0

    @staticmethod
    def default_probation_pl():
        return 0

    @staticmethod
    def default_probation_al():
        return 0

    @staticmethod
    def default_confirmed_dl():
        return 0

    @staticmethod
    def default_confirmed_pl():
        return 0

    @staticmethod
    def default_confirmed_al():
        return 0
