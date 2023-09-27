# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class OperacionesMinori(models.Model):
    _name = 'method_conector_marcas.operaciones_minori'
    _description = 'Tipos de operaciones de minori'
    
    name = fields.Char(string='Nombre')
    operacion_id = fields.Integer(string='ID Operacion')



class SolicitudIngreso(models.Model):
    _inherit = 'stock.picking'

    minori_po_id = fields.Integer(string='Id Solicitud Minori')
    es_traspaso_minori = fields.Boolean(string='Envío productos a Minori?')
    operacion_minori_id = fields.Many2one(comodel_name='method_conector_marcas.operaciones_minori', string='Operación Minori')


    @api.one
    def sync_po(self):    
        if self.es_traspaso_minori==True:
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
                    {'limit':1})
            
            if not po_id and not self.minori_po_id:
    #Partner            
                partner_id=models.execute_kw(db, uid, password,
                    'res.partner', 'search_read',
                    [[['vat', '=', datos.partner_id.vat]]],
                    {'limit':1})
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
                        {'limit':1})
                # for r in partner_id:
                partner_id=partner_id[0]['id']

    #Orden de compra
                order_line=[]
                for l in self.move_ids_without_package:
                    if l.product_minori_id:
                        product_id=l.product_minori_id.product_minori_id
                        product_id_id=l.product_minori_id.product_minori_id
                        product_uom=l.product_minori_id.product_minori_uom_id
                    else:
                        # raise Warning("EL producto %s" % l.product_id.name +' '+l.product_id.default_code +' no existe en Minori')                    
                            # product_template_id=l.product_id.product_tmpl_id.sync_productos()
                        product_id=models.execute_kw(db, uid, password,
                                'product.product', 'search_read',
                                [[['default_code', '=', l.product_id.default_code]]],
                                {'limit':1})
                        if not product_id:                        
                            product_template_id=l.product_id.product_tmpl_id.sync_productos()
                            product_id=models.execute_kw(db, uid, password,
                                    'product.product', 'search_read',
                                    [[['default_code', '=', l.product_id.default_code]]],
                                    {'limit':1})

                        product_id_id=product_id[0]['id']
                        product_uom=product_id[0]['uom_id'][0]

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
                    'picking_type_id':self.operacion_minori_id.operacion_id
                }
                po_id = models.execute_kw(db, uid, password, 'purchase.order', 'create', [values])
                self.minori_po_id=po_id

            else:
                raise Warning("Este documento ya fue sincronizado con Minori!")
        else:
            raise Warning("Debe marcas la opción: Envío productos a Minor, para continuar!")