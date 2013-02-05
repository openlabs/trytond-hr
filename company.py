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
    # Attendance specific config
    early_departure_time = fields.Time('Early Departure Time', states=STATES)
    allowed_early_departures = fields.Integer(
        'Allowed Early Departures (per month)', states=STATES
    )
    late_coming_time = fields.Time('Late Coming Time', states=STATES)
    allowed_late_comings = fields.Integer(
        'Allowed Late Comings (per month)', states=STATES
    )

    @staticmethod
    def default_allowed_early_departures():
        return 2

    @staticmethod
    def default_allowed_late_comings():
        return 2

    @staticmethod
    def default_active():
        return True
