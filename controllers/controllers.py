# -*- coding: utf-8 -*-
from odoo import http

# class MethodConectorMarcas(http.Controller):
#     @http.route('/method_conector_marcas/method_conector_marcas/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/method_conector_marcas/method_conector_marcas/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('method_conector_marcas.listing', {
#             'root': '/method_conector_marcas/method_conector_marcas',
#             'objects': http.request.env['method_conector_marcas.method_conector_marcas'].search([]),
#         })

#     @http.route('/method_conector_marcas/method_conector_marcas/objects/<model("method_conector_marcas.method_conector_marcas"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('method_conector_marcas.object', {
#             'object': obj
#         })