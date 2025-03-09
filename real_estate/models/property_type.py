from odoo import api, fields, models


class PropertyType(models.Model):
    _name = 'real.estate.property.type'
    _description = 'Real Estate Property Type'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    property_ids = fields.One2many(
        comodel_name='real.estate.property',
        inverse_name='property_type_id',
        string='Properties',
    )
    property_count = fields.Integer(
        string='Property Count',
        compute='_compute_property_count',
    )
    description = fields.Text(
        string='Description',
    )
    color = fields.Integer(
        string='Color Index',
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Property type name already exists!'),
    ]

    @api.depends('property_ids')
    def _compute_property_count(self):
        for record in self:
            record.property_count = len(record.property_ids)

    def action_view_properties(self):
        self.ensure_one()
        return {
            'name': f'Properties of {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'real.estate.property',
            'view_mode': 'kanban,tree,form',
            'domain': [('property_type_id', '=', self.id)],
            'context': {'default_property_type_id': self.id},
        }
