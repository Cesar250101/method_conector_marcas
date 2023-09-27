# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class StockMove(models.Model):
    _inherit = 'stock.move'

    product_minori_id = fields.Many2one(comodel_name='product.minori', string='Producto Minori')
    es_traspaso_minori = fields.Boolean(string='Envío productos a Minori?',related='picking_id.es_traspaso_minori')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_minori_id=self.env['product.minori'].search([('product_id','=',self.product_id.id)])

    
