# -*- coding: utf-8 -*-
"""
    Company

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval

__all__ = ['Department']

STATES = {
    'readonly': ~Eval('active', True),
}

class Department(ModelSQL, ModelView):
    "Company Department"
    __name__ = 'company.department'

    name = fields.Char('Name', required=True, states=STATES)
    active = fields.Boolean('Active')
    company = fields.Many2One(
        'company.company', 'Company', required=True, states=STATES,
    )
    parent = fields.Many2One(
        'company.department', 'Parent',
        domain=[
            ('company', '=', Eval('company')),
            ('id', '!=', Eval('id'))
        ],
        depends=['company', 'id'], states=STATES,
    )

    @staticmethod
    def default_active():
        return True
