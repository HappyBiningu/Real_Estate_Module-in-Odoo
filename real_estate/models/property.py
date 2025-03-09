from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta


class Property(models.Model):
    _name = 'real.estate.property'
    _description = 'Real Estate Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(
        string='Title',
        required=True,
        tracking=True,
    )
    description = fields.Text(
        string='Description',
        tracking=True,
    )
    postcode = fields.Char(
        string='Postcode',
        tracking=True,
    )
    date_availability = fields.Date(
        string='Available From',
        default=lambda self: fields.Date.today() + timedelta(days=90),
        tracking=True,
    )
    expected_price = fields.Float(
        string='Expected Price',
        required=True,
        tracking=True,
    )
    selling_price = fields.Float(
        string='Selling Price',
        readonly=True,
        copy=False,
        tracking=True,
    )
    bedrooms = fields.Integer(
        string='Bedrooms',
        default=2,
        tracking=True,
    )
    living_area = fields.Integer(
        string='Living Area (sqm)',
        tracking=True,
    )
    facades = fields.Integer(
        string='Facades',
        tracking=True,
    )
    garage = fields.Boolean(
        string='Garage',
        tracking=True,
    )
    garden = fields.Boolean(
        string='Garden',
        tracking=True,
    )
    garden_area = fields.Integer(
        string='Garden Area (sqm)',
        tracking=True,
    )
    garden_orientation = fields.Selection(
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        string='Garden Orientation',
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),
            ('rented', 'Rented'),
        ],
        string='Status',
        required=True,
        default='new',
        tracking=True,
        copy=False,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    property_type_id = fields.Many2one(
        comodel_name='real.estate.property.type',
        string='Property Type',
        tracking=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True,
    )
    buyer_id = fields.Many2one(
        comodel_name='res.partner',
        string='Buyer',
        readonly=True,
        copy=False,
        tracking=True,
    )
    tag_ids = fields.Many2many(
        comodel_name='real.estate.property.tag',
        string='Tags',
    )
    offer_ids = fields.One2many(
        comodel_name='real.estate.property.offer',
        inverse_name='property_id',
        string='Offers',
    )
    total_area = fields.Integer(
        string='Total Area (sqm)',
        compute='_compute_total_area',
        store=True,
    )
    best_offer = fields.Float(
        string='Best Offer',
        compute='_compute_best_offer',
        store=True,
    )
    address = fields.Char(
        string='Address',
        tracking=True,
    )
    city = fields.Char(
        string='City',
        tracking=True,
    )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country',
        tracking=True,
    )
    property_image_ids = fields.One2many(
        comodel_name='real.estate.property.image',
        inverse_name='property_id',
        string='Property Images',
    )
    main_image_id = fields.Many2one(
        comodel_name='real.estate.property.image',
        string='Main Image',
        domain="[('property_id', '=', id)]",
    )
    amenities = fields.Text(
        string='Amenities',
        help="List of amenities available with the property",
        tracking=True,
    )
    furnished = fields.Boolean(
        string='Furnished',
        tracking=True,
    )
    
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_offer = max(record.offer_ids.mapped('price'))
            else:
                record.best_offer = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError(_("Canceled properties cannot be sold."))
            if not record.buyer_id:
                raise UserError(_("You cannot sell a property without a buyer."))
            record.state = 'sold'
        return True

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(_("Sold properties cannot be canceled."))
            record.state = 'canceled'
        return True
    
    def action_mark_as_rented(self):
        for record in self:
            if record.state in ['sold', 'canceled']:
                raise UserError(_("Properties that are sold or canceled cannot be rented."))
            record.state = 'rented'
        return True

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price and record.selling_price < record.expected_price * 0.9:
                raise ValidationError(_("The selling price cannot be lower than 90% of the expected price."))

    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_sold_or_canceled(self):
        for record in self:
            if record.state in ['sold', 'offer_accepted']:
                raise UserError(_("You cannot delete a property that is sold or has an accepted offer."))
                
    def action_send_email(self):
        """Send email about this property to interested parties"""
        self.ensure_one()
        # This would be implemented with email templates and email sending logic
        # For now, it's just a placeholder
        return {
            'type': 'ir.actions.act_window_close'
        }


class PropertyImage(models.Model):
    _name = 'real.estate.property.image'
    _description = 'Property Image'
    _order = 'sequence, id'

    name = fields.Char(
        string='Name',
        required=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    image = fields.Binary(
        string='Image',
        attachment=True,
        required=True,
    )
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string='Property',
        required=True,
        ondelete='cascade',
    )
    description = fields.Text(
        string='Description',
    )
