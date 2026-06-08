from odoo import api, models, fields
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Parking Management System"

    name = fields.Char(string="Spot Number", required=True)
    zone = fields.Char(string="Zone")
    hourly_rate = fields.Float(string="Hourly Rate ($)", default=2.0)
    
    state = fields.Selection(selection=[
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("occupied", "Occupied"),
        ("maintenance", "Maintenance")
    ], default="available", required=True, string="Status")
    
    license_plate = fields.Char(string="License Plate")
    spot_type = fields.Selection(selection=[
        ("standard", "Standard"),
        ("handicap", "Handicap"),
        ("ev", "Electric Vehicle (EV)"),
        ("motorcycle", "Motorcycle"),
        ("staff", "Staff")
    ], default="standard", string="Spot Type")
    
    customer_name = fields.Char(string="Customer Name")
    reservation_start = fields.Datetime(string="Reservation Start", default=fields.Datetime.now)
    reservation_end = fields.Datetime(string="Reservation End")
    
    duration_hours = fields.Float(string="Duration (Hours)", compute="_compute_duration", store=True)
    total_price = fields.Float(string="Total Price ($)", compute="_compute_total_price", store=True)
    
    @api.depends("reservation_start", "reservation_end")
    def _compute_duration(self):
        for record in self:
            if record.reservation_start and record.reservation_end:
                delta = record.reservation_end - record.reservation_start
                record.duration_hours = max(delta.total_seconds() / 3600.0, 0)
            else:
                record.duration_hours = 0
    
    @api.depends("duration_hours", "hourly_rate")
    def _compute_total_price(self):
        for record in self:
            record.total_price = record.duration_hours * record.hourly_rate
    
    def action_reserve(self):
        for record in self:
            if record.state != "available":
                raise UserError("Only available spots can be reserved.")
            if not record.customer_name:
                raise UserError("Please enter customer name before reserving.")
            if not record.license_plate:
                raise UserError("Please enter license plate before reserving.")
            if not record.reservation_end:
                raise UserError("Please enter reservation end time.")
            if record.reservation_end <= record.reservation_start:
                raise UserError("End time must be after start time.")
            record.state = "reserved"
    
    def action_occupy(self):
        for record in self:
            if record.state != "reserved":
                raise UserError("Only reserved spots can be marked as occupied.")
            record.state = "occupied"
    
    def action_release(self):
        for record in self:
            if record.state not in ["reserved", "occupied"]:
                raise UserError("Only reserved or occupied spots can be released.")
            record.state = "available"
            record.customer_name = False
            record.license_plate = False
            record.reservation_start = fields.Datetime.now()
            record.reservation_end = False
    
    def action_maintenance(self):
        for record in self:
            if record.state == "maintenance":
                raise UserError("Spot already in maintenance.")
            record.state = "maintenance"
    
    def action_available(self):
        for record in self:
            if record.state != "maintenance":
                raise UserError("Only maintenance spots can be set back to available.")
            record.state = "available"
    
    def _auto_release_expired_reservations(self):
        expired_spots = self.search([
            ('state', '=', 'reserved'),
            ('reservation_end', '<', fields.Datetime.now())
        ])
        count = 0
        for spot in expired_spots:
            spot.state = 'available'
            spot.customer_name = False
            spot.license_plate = False
            spot.reservation_end = False
            count += 1
            _logger.info(f"Auto-released expired reservation for spot: {spot.name}")
        return count