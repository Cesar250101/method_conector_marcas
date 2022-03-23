# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xmlrpc.client
from datetime import datetime
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class ModuleName(models.Model):
    _inherit = 'res.company'
    url_method = fields.Char(string='URL Servidor Method',default="http://erp.method.cl")
    bd_method=fields.Char(string='Base de Datos Method',default="method")
    user_method=fields.Char(string='Usuario Method',default="cesar@method.cl")
    password_method=fields.Char(string='Password Usuario Method',default="2010")
    usuario_admin = fields.Char(string='Usuario Administrador', default="cesar@method.cl")    
    pos_category = fields.Char(string='Marca')    



class SolicitudIngreso(models.Model):
    _inherit = 'product.template'

    product_minori_id = fields.Integer(string='ID Producto Minori')
    product_stock_minori = fields.Integer(string='Stock Minori')
    
    

    @api.one
    def sync_productos(self):    
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
        if self.default_code:
            product_id=models.execute_kw(db, uid, password,
                    'product.template', 'search_read',
                    [[['default_code', '=', self.default_code]]],
                    [])
            if product_id:                        
                product_id=product_id[0]["id"]
            else:
    #Categoria            
                categoria_id=models.execute_kw(db, uid, password,
                    'product.category', 'search_read',
                    [[['name', '=', self.categ_id.name]]],
                    [])
                
                if not categoria_id:
                    categoria_id = models.execute_kw(db, uid, password, 'product.category', 'create', 
                                [{
                                    'name': self.categ_id.name,
                                }])
                    categoria_id=models.execute_kw(db, uid, password,
                        'product.category', 'search_read',
                        [[['name', '=', self.categ_id.name]]],
                        [])

                for c in categoria_id:
                    categoria_id=c['id']

    #Categoria POS
                pos_category_id=models.execute_kw(db, uid, password,
                    'pos.category', 'search_read',
                    [[['name', '=', marca]]],
                    [])
                if not pos_category_id:
                    pos_category_id = models.execute_kw(db, uid, password, 'pos.category', 'create', 
                                [{
                                    'name': marca,
                                }])
                    pos_category_id=models.execute_kw(db, uid, password,
                        'pos.category', 'search_read',
                        [[['name', '=', marca]]],
                        [])

                for pc in pos_category_id:
                    pos_category_id=pc['id']
    #Marca
                marca_id=models.execute_kw(db, uid, password,
                    'method_minori.marcas', 'search_read',
                    [[['name', '=', marca]]],
                    [])
                if not marca_id:
                    marca_id = models.execute_kw(db, uid, password, 'method_minori.marcas', 'create', 
                                [{
                                    'name': marca,
                                }])
                    marca_id=models.execute_kw(db, uid, password,
                        'method_minori.marcas', 'search_read',
                        [[['name', '=', marca]]],
                        [])

                for m in marca_id:                        
                    marca_id=m['id']
                values={
                    'name': self.name,
                    'default_code':self.default_code,
                    'list_price':self.list_price,
                    'type':self.type,
                    'categ_id':categoria_id,
                    'uom_id':self.uom_id.id,
                    'uom_po_id':self.uom_po_id.id,
                    'standard_price':self.standard_price,
                    'available_in_pos':True,
                    'pos_categ_id':pos_category_id,
                    'marca_id':marca_id
                    
                }
                product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [values])
                print(product_id)                        
        else:
            raise Warning("Debe ingresar una referecia interna para el producto!!")
    
    @api.one
    def sync_stock_productos(self):
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

        product_id=models.execute_kw(db, uid, password,
                        'product.template', 'search_read',
                        [[['default_code', '=', self.default_code]]],
                        [])                        
        if product_id:
            for pi in product_id:
                stock=pi['qty_available']
            self.product_stock_minori=stock