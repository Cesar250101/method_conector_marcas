# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class SolicitudIngreso(models.Model):
    _inherit = 'stock.picking'

    minori_po_id = fields.Integer(string='Id Solicitud Minori')


    @api.one
    def sync_po(self):    
        contexto=self.env.context
        datos=self.company_id
        url = datos.url_method
        db = datos.bd_method
        username = datos.user_method
        password = datos.password_method
        marca=datos.pos_category

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})

        po_id=models.execute_kw(db, uid, password,
                'purchase.order', 'search_read',
                [[['id', '=', self.minori_po_id]]],
                [])
        
        if not po_id and not self.minori_po_id:
#Partner            
            partner_id=models.execute_kw(db, uid, password,
                'res.partner', 'search_read',
                [[['vat', '=', datos.partner_id.vat]]],
                [])
            if not partner_id:
                vals={
                        'name': datos.name,
                        'document_type':datos.document_type_id.id,
                        'document_number': datos.document_number,
                        'street':datos.street,
                        'city':datos.city,
                        'city_id':datos.city_id.id,
                        'vat':datos.partner_id.vat
                    }
                partner_id = models.execute_kw(db, uid, password, 'res.partner', 'create', 
                            [vals])
                partner_id=models.execute_kw(db, uid, password,
                    'res.partner', 'search_read',
                    [[['vat', '=', datos.partner_id.vat]]],
                    [])
            for r in partner_id:
                partner_id=r['id']

#Orden de compra
            order_line=[]
            for l in self.move_ids_without_package:
                product_id=models.execute_kw(db, uid, password,
                    'product.product', 'search_read',
                    [[['default_code', '=', l.product_id.default_code]]],
                    [])

                if not product_id:
                    raise Warning("EL producto %s" % l.product_id.name +' '+l.product_id.default_code +' no existe en Minori')
                else:
                    for p in product_id:
                        product_id_id=p['id']
                        product_uom=p['uom_id'][0]

                order_line.append(
                    (0, 0, {
                                "product_id": product_id_id,
                                "product_uom": product_uom,
                                "product_qty":l.quantity_done,
                                "price_unit":l.price_untaxed,
                                "name":l.product_id.name,   
                                "date_planned":self.scheduled_date,
                    }))

            values={
                'name': self.name +' '+marca,
                'partner_id':partner_id,   
                'date_order':self.scheduled_date,
                "date_planned":self.scheduled_date,
                "order_line":order_line,
            }
            po_id = models.execute_kw(db, uid, password, 'purchase.order', 'create', [values])
            self.minori_po_id=po_id

        else:
            raise Warning("Este documento ya fue sincronizado con Minori!")