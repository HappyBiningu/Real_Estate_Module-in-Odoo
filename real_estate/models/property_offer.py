from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class PropertyOffer(models.Model):
    _name = 'real.estate.property.offer'
    _description = 'Real Estate Property Offer'
    _order = 'price desc'
    _rec_name = 'partner_id'

    price = fields.Float(
        string='Price',
        required=True,
    )
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
            ('pending', 'Pending'),
        ],
        string='Status',
        default='pending',
        copy=False,
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        required=True,
    )
    property_id = fields.Many2one(
        comodel_name='real.estate.property',
        string='Property',
        required=True,
        ondelete='cascade',
    )
    validity = fields.Integer(
        string='Validity (days)',
        default=7,
    )
    date_deadline = fields.Date(
        string='Deadline',
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
        store=True,
    )
    create_date = fields.Datetime(
        string='Creation Date',
        readonly=True,
    )
    
    property_state = fields.Selection(
        related='property_id.state',
        string='Property Status',
    )
    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        string='Property Type',
    )

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                create_date = fields.Date.from_string(offer.create_date)
                offer.date_deadline = create_date + timedelta(days=offer.validity)
            else:
                offer.date_deadline = fields.Date.today() + timedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            if offer.create_date and offer.date_deadline:
                create_date = fields.Date.from_string(offer.create_date)
                offer.validity = (offer.date_deadline - create_date).days

    def action_accept(self):
        for offer in self:
            # Check if there's already an accepted offer for this property
            if any(o.status == 'accepted' and o.id != offer.id for o in offer.property_id.offer_ids):
                raise UserError(_("Another offer has already been accepted for this property."))
            
            offer.status = 'accepted'
            offer.property_id.write({
                'state': 'offer_accepted',
                'selling_price': offer.price,
                'buyer_id': offer.partner_id.id,
            })
            # Set other offers as refused
            (offer.property_id.offer_ids - offer).write({'status': 'refused'})
        return True

    def action_refuse(self):
        for offer in self:
            offer.status = 'refused'
        return True

    @api.model
    def create(self, vals):
        property_id = self.env['real.estate.property'].browse(vals.get('property_id'))
        
        # Check if property is in a valid state to receive offers
        if property_id.state in ['sold', 'canceled']:
            raise UserError(_("You cannot make an offer for a sold or canceled property."))
        
        # Check if the offer price is higher than existing offers
        if property_id.offer_ids:
            max_offer = max(property_id.offer_ids.mapped('price'))
            if vals.get('price', 0) <= max_offer:
                raise UserError(_("The offer must be higher than %.2f") % max_offer)
        
        offer = super(PropertyOffer, self).create(vals)
        
        # Update property state when receiving first offer
        if property_id.state == 'new':
            property_id.state = 'offer_received'
        
        return offer
