# -*- coding: utf-8 -*-
"""
    configuration

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, ModelSingleton, fields

__all__ = ['Configuration']


class Configuration(ModelSingleton, ModelSQL, ModelView):
    'Employee Configuration'
    __name__ = 'company.employee.configuration'

    employee_sequence = fields.Property(fields.Many2One(
            'ir.sequence', 'Employee Sequence',
            domain=[('employee_id', '=', 'company.employee')]
    ))
