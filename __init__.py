# -*- coding: utf-8 -*-
"""
    __init__

    :copyright: © 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool
from .company import *


def register():
    Pool.register(
        Department,
        Responsibility,
        Language,
        Academics,
        Skill,
        Team,
        StaffDetails,
        module='hr', type_='model')
