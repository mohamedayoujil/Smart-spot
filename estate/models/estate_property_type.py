from odoo import api, models, fields

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Parking Zones"

    name = fields.Char(string="Zone Name", required=True)
    description = fields.Text(string="Description")