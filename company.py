# -*- coding: utf-8 -*-
"""
    Company

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval, Bool
from trytond.pool import Pool
__all__ = [
    'Department', 'Responsibility', 'Language', 'Academics',
    'StaffDetails', 'Skill', 'Team', 'TransferProposal', 'TransferRemark',
]

STATES = {
    'readonly': ~Eval('active', True),
}


class Department(ModelView, ModelSQL):
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


class Responsibility(ModelSQL, ModelView):
    "Responsibility"
    __name__ = "company.employee.responsibility"

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True,
    )
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class Team(ModelSQL, ModelView):
    "Team"
    __name__ = "company.employee.team"

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True,
    )
    name = fields.Char('Name', required=True)
    description = fields.Text('Description')


class Language(ModelSQL, ModelView):
    "Language"
    __name__ = "company.employee.language"

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True,
    )
    language = fields.Many2One(
        'ir.lang', 'Language', required=True,
    )
    mother_tounge = fields.Boolean('Mother Tounge')
    read = fields.Boolean('Read')
    write = fields.Boolean('Write')
    speak = fields.Boolean('Speak')

    @classmethod
    def __setup__(cls):
        super(Language, cls).__setup__()
        cls._sql_constraints = [
            ('code_uniq', 'UNIQUE(employee, language)',
             'Employee should have unique language')
        ]


class Skill(ModelSQL, ModelView):
    "Skill"
    __name__ = "company.employee.skill"

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True,
    )
    name = fields.Char('Name', required=True)


class Academics(ModelSQL, ModelView):
    "Academics"
    __name__ = "company.employee.academics"

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True,
    )
    institution = fields.Char('Institution', required=True)
    major = fields.Char('Major', required=True)
    level = fields.Char('Level')
    year = fields.Integer('Year', required=True)
    percentage = fields.Numeric('Percentage', digits=(2, 2), required=True)


class StaffDetails(ModelSQL, ModelView):
    "Staff Details"
    __name__ = "company.employee.staff_details"

    name = fields.Many2One('company.employee', 'Name', required=True)
    party = fields.Function(
        fields.Many2One('party.party', 'Party', on_change_with=['name']),
        'get_party',
    )
    photo = fields.Binary('Photo')
    state = fields.Selection([
            ('current', 'Current'),
            ('retired', 'Retired'),
            ('closed', 'Closed'),
        ], 'State', required=True,
    )
    first_name = fields.Char('First Name', required=True)
    middle_name = fields.Char('Middle Name')
    last_name = fields.Char('Last Name', required=True)
    employee_id = fields.Char('Employee ID', readonly=True)
    manager = fields.Many2One('company.employee', 'Manager')
    permanent_address = fields.Many2One(
        'party.address', 'Permanent Address', required=True,
        domain=[('party', '=', Eval('party'))],
        depends=['party'],
    )
    present_address = fields.Many2One(
        'party.address', 'Present Address', required=True,
        domain=[('party', '=', Eval('party'))],
        depends=['party'],
    )
    addresses = fields.Function(
        fields.One2Many('party.address', 'party', 'Addresses'),
        'get_addresses', 'set_addresses'
    )
    contact_mechanisms = fields.Function(
        fields.One2Many('party.contact_mechanism', 'party', 'Contact Mechanisms'),
        'get_contact_mechanisms', 'set_contact_mechanisms'
    )
    sex = fields.Selection([
            ('male', 'Male'),
            ('female', 'Female')
        ], 'Sex', required=True
    )
    date_of_birth = fields.Date('Date of Birth', required=True)
    place_of_birth = fields.Char('Place of Birth', required=True)
    marital_status = fields.Selection([
            ('single', 'Single'),
            ('married', 'Married')
        ], 'Marital Status', required=True
    )
    wedding_date = fields.Date(
        'Wedding Date',
        states={
            'invisible': Eval('marital_status') == 'single',
            'required': Eval('marital_status') == 'married'
        },
    )
    marriage_license = fields.Char(
        'Marriage License',
        states={
            'invisible': Eval('marital_status') == 'single',
            'required': Eval('marital_status') == 'married'
        },
    )
    nationality = fields.Many2One(
        'country.country', 'Nationality', required=True,
    )
    native_state = fields.Many2One(
        'country.subdivision', 'Native State',
        domain=[('country', '=', Eval('nationality'))],
        depends=['nationality'],
    )
    language_skills = fields.One2Many(
        'company.employee.language', 'employee', 'Language Skills'
    )
    religion = fields.Char('Religion') #TODO: many2one to employee.religion
    denomination = fields.Char('Denomination') #TODO: m2o to employee.denomination
    driving_license = fields.Char('Driving License')
    driving_license_validity = fields.Date(
        'Driving License Validity',
        states={'required': Bool(Eval('driving_license'))},
    )
    passport_number = fields.Char('Passport Number')
    passport_validity = fields.Date(
        'Passport Validity',
        states={'required': Bool(Eval('passport_number'))},
    )
    academics = fields.One2Many(
        'company.employee.academics', 'employee', 'Academics'
    )
    skills = fields.One2Many(
        'company.employee.skill', 'employee', 'Skills'
    )
    responsibilities = fields.One2Many(
        'company.employee.responsibility', 'employee', 'Responsibilities'
    )
    team = fields.One2Many(
        'company.employee.team', 'employee', 'Team'
    )
    transfers = fields.One2Many(
        'employee.transfer.proposal', 'employee',
        'Promotion / Transfer Proposals'
    )

    @staticmethod
    def default_state():
        return 'current'

    @staticmethod
    def default_sex():
        return 'male'

    @staticmethod
    def default_marital_status():
        return 'single'

    def get_party(self, name):
        return self.name.party.id

    def get_addresses(self, name):
        """
        Return all the addresses of the party as the address of the employee
        """
        return map(int, self.party.addresses)

    @classmethod
    def set_addresses(cls, records, name, value=None):
        """
        Set the address as the address of the party
        """
        Party = Pool().get('party.party')

        for record in records:
            Party.write([record.party], {'addresses': value})

    def on_change_with_party(self):
        return self.name.party.id

    def get_contact_mechanisms(self, name):
        """
        Return all the contact_mechanisms of the party as the
        contact_mechanism of the employee
        """
        return map(int, self.party.contact_mechanisms)

    @classmethod
    def set_contact_mechanisms(cls, records, name, value=None):
        """
        Set the contact_mechanism as the contact_mechanism of the party
        """
        Party = Pool().get('party.party')

        for record in records:
            Party.write([record.party], {'contact_mechanisms': value})


class TransferProposal(ModelSQL, ModelView):
    "Employee Promotion and Transfer Proposal"
    __name__ = 'employee.transfer.proposal'
    _rec_name = 'employee'

    employee = fields.Many2One(
        'company.employee.staff_details', 'Employee', required=True
    )
    proposed_company = fields.Many2One(
        'company.company', 'Proposed Company', required=True
    )
    proposed_department = fields.Many2One(
        'company.department', 'Proposed Department', domain=[
            ('company', '=', Eval('proposed_company'))
        ], required=True
    )
    proposed_allowance = fields.Numeric('Proposed Allowance', required=True)
    proposed_doj = fields.Date('Proposed Date of Joining', required=True)
    remarks = fields.One2Many(
        'employee.transfer.remark', 'proposal', 'Remarks'
    )


class TransferRemark(ModelSQL, ModelView):
    "Employe Transfer Remark"
    __name__ = 'employee.transfer.remark'
    _rec_name = 'proposal'

    employee = fields.Many2One(
        'company.employee', 'Employee', required=True
    )
    proposal = fields.Many2One(
        'employee.transfer.proposal', 'Proposal', required=True
    )
    date = fields.Date('Date', required=True)
    comment = fields.Text('Comment')
    remark = fields.Selection([
        ('recommended', 'Recommended'),
        ('not_recommended', 'Not Recommended'),
        ('average', 'Average'),
        ('rejected', 'Rejected')
    ], 'Remark', required=True)

    @staticmethod
    def default_remark():
        return 'recommended'

    @staticmethod
    def default_date():
        Date = Pool().get('ir.date')
        return Date.today()
