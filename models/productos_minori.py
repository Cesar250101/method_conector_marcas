# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class ProductosMinori(models.Model):
    _name = 'product.minori'

    product_minori_id = fields.Integer(string='ID Producto Minori')    
    name = fields.Char(string='Nombre Producto Minori')
    product_minori_uom_id = fields.Integer(string='Unidad de Medida')
    product_minori_categ_id = fields.Integer(string='Categoría Producto')
    product_minori_default_code = fields.Char(string='SKU')
    product_id = fields.Many2one(comodel_name='product.product', string='Producto')

    @api.model
    def get_product_minori(self):    
        contexto=self.env.user
        datos=contexto.company_id
        url = datos.url_method
        db = datos.bd_method
        username = datos.user_method
        password = datos.password_method
        marca=datos.pos_category
        
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        uid = common.authenticate(db, username, password, {})

        # product_minori_ids=models.execute_kw(db, uid, password,
        #             'product.product', 'search_read',
        #             [[]],{'fields': ['display_name', 'id','uom_id','categ_id','default_code'],'limit':10})
        product_minori_ids=models.execute_kw(db, uid, password,
                    'product.product', 'search_read',
                    [[]],{'fields': ['display_name', 'id','uom_id','categ_id','default_code']})

        # print(product_minori_ids)
        # print()
        for i in product_minori_ids:
            product_minori_id=self.search([('product_minori_id','=',i['id'])])
            if not product_minori_id:
                values={
                    'product_minori_id':i['id'],
                    'name':i['display_name'],
                    'product_minori_uom_id':i['uom_id'][0],
                    'product_minori_categ_id':i['categ_id'][0],
                    'product_minori_default_code':i['default_code']
                }
                create_id=self.create(values)
                product_product_id=self.env['product.product'].search([('default_code','like',i['default_code'])],limit=1)
                if product_product_id:
                    # product_product_id.product_minori_id=i['id']
                    create_id.product_id=product_product_id.id

