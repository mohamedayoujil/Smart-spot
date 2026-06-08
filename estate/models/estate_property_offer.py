from odoo import api, models, fields
from odoo.exceptions import UserError

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Parking Bookings"

    property_id = fields.Many2one("estate.property", string="Parking Spot", required=True)
    partner_id = fields.Many2one("res.partner", string="Customer Name")
    price = fields.Float(string="Total Fee")
    state = fields.Selection(selection=[
        ("active", "Active"),
        ("accepted", "Completed"),
        ("refused", "Cancelled")
    ], default="active")
    
    def action_accept(self):
        for record in self:
            record.state = "accepted"
            if record.property_id:
                record.property_id.action_release()
    
    def action_refuse(self):
        for record in self:
            record.state = "refused"