from odoo import models, api
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class accountInvoice(models.Model):
    _inherit = 'account.move'

    pass