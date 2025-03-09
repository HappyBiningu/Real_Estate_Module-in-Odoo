from odoo import fields, models


class PropertyTag(models.Model):
    _name = 'real.estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    color = fields.Integer(
        string='Color Index',
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Tag name already exists!'),
    ]
