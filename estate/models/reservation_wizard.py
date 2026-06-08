from odoo import api, models, fields
from odoo.exceptions import UserError

class ReservationWizard(models.TransientModel):
    _name = "reservation.wizard"
    _description = "Reservation Wizard"

    reservation_start = fields.Datetime(string="Reservation Start", required=True, default=fields.Datetime.now)
    reservation_end = fields.Datetime(string="Reservation End", required=True)
    customer_name = fields.Char(string="Customer Name", required=True)
    
    def action_confirm_reservation(self):
        active_id = self.env.context.get('active_id')
        spot = self.env['estate.property'].browse(active_id)
        
        if not spot:
            raise UserError("No parking spot found.")
        
        if spot.state != "available":
            raise UserError("This spot is not available for reservation.")
        
        # Update the spot
        spot.write({
            'state': 'reserved',
            'reservation_start': self.reservation_start,
            'reservation_end': self.reservation_end,
            'reserved_by': self.customer_name,
        })
        
        # Create a booking record
        self.env['estate.property.offer'].create({
            'property_id': spot.id,
            'partner_id': self.customer_name,
            'price': 0,
            'state': 'active',
        })
        
        return {'type': 'ir.actions.act_window_close'}