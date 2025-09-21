from odoo import http
from odoo.http import request
import json
import logging
import traceback


_logger = logging.getLogger(__name__)

class ProductTemplateController(http.Controller):
    @http.route('/product', type='http', auth='public', methods=['GET'], cors='*')
    def get_products(self):
        try:
            products = request.env['product.template'].sudo().search([('active', '=', True)])
            for product in products:
                fields = product.fields_get()
                for field_name in fields:
                    value = getattr(product, field_name, None)
                    print(f"{field_name}: {value}")
                print("-----")
            # product_list = [{'id': p.id, 'name': p.name or '', 'description':p.description,'weight':p.weight,} for p in products]
            product_list = [{
                'id': p.id,   #Unique product identifier
                'name': p.name or '',
                'description': p.description or '',
                'description_sale': p.description_sale or '', #Long description shown to users
                'ecommerce description': p.description_ecommerce or '',
                # 'care_guide_id':p.care_guide_id.name if p.care_guide_id else '' , #Care guide
                'material_id': p.material_id.name if p.material_id else '',  # Material
                'care_guide_id': p.care_guide_id.name if p.care_guide_id else '',  # Care guide
                'items_included_id': p.items_included_id.name if p.items_included_id else '',  # Care guide
                'product_note_id': p.product_note_id or '',  # Care guide
                'weight': p.weight or 0.0,
                'volume': p.volume or 0.0,
                'compare to price': p.compare_list_price or 0.0,
                'list_price': p.list_price or 0.0,
                'default_code': p.default_code or '',
                # 'image_url': f"/web/image/product.template/{p.id}/image_1920",
                'image_url': f"/web/image/product.template/{p.id}/image_1920" if p.image_1920 else '',
                'additional_media': [{
                    'id': img.id,
                    'name': img.name,
                    'image_url': f"/web/image/product.image/{img.id}/image_1920" if img.image_1920 else '',
                    'video_url': img.video_url or '',
                } for img in request.env['product.image'].sudo().search([
                    ('product_tmpl_id', '=', p.id),
                    ('image_1920', '!=', p.image_1920)  # Filter out duplicate of main image
                ])],
                'customer_reviews': [{
                     'name': review.partner_id.name if review.partner_id else '',
                    'rating': review.rating or 0.0,
                    'date': review.create_date.strftime('%Y-%m-%d') if review.create_date else '',
                    'review': review.feedback or ''
                } for review in request.env['rating.rating'].sudo().search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', p.id),
                    ('rating', '!=', 0),
                ])],


                'tags': [tag.name for tag in p.product_tag_ids] if p.product_tag_ids else [],  # 👈 Here you get tags
                'public_categories': [{'id': cat.id, 'name': cat.name} for cat in
                                      p.public_categ_ids] if p.public_categ_ids else [],
                'type': p.type or '',
                'uom_id': p.uom_id.name if p.uom_id else '',
                'categ_id': p.categ_id.name if p.categ_id else '', #Product category
                'active': p.active,

                'out_of_stock_message': p.out_of_stock_message or '',#
                'on_hand_qty': p.qty_available or 0.0,
                'show_availability':p.show_availability, #Whether to show availability
                'is_published': p.is_published, #Whether product is published on website
                'variant_available': len(p.product_variant_ids) or '0',
                'variants': [{
                    'id': variant.id,
                    'name': variant.name,
                    'price': variant.list_price,
                    'internal reference': variant.default_code,
                    'attribute_values': [{
                        'attribute': attr_value.attribute_id.name,
                        'value': attr_value.name
                    } for attr_value in variant.product_template_variant_value_ids]
                } for variant in p.product_variant_ids],

                'attributes': [
                    {
                        'id': attr.id,
                        'name': attr.name,
                        'values': [
                            {
                                'id': val.id,
                                'name': val.name
                            }
                            for val in p.product_variant_ids.mapped('product_template_attribute_value_ids')
                            .filtered(lambda x: x.attribute_id.id == attr.id)
                        ]
                    }
                    for attr in p.product_variant_ids.mapped('product_template_attribute_value_ids.attribute_id')
                ],
            } for p in products]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'Product list fetched successfully',
                    'data': product_list
                }),
                headers={'Content-Type': 'application/json'}
            )
        except Exception as e:
            _logger.error("Error fetching products: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch products at the moment. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )



_logger = logging.getLogger(__name__)

class ProductByCategoryNameController(http.Controller):

    @http.route('/products/category', type='http', auth='public', methods=['GET'], cors='*')
    def get_all_categories(self):
        try:
            categories = request.env['product.public.category'].sudo().search([])
            category_list = [{'id': c.id, 'name': c.name} for c in categories]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'All public categories fetched successfully.',
                    'data': category_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            import traceback
            _logger.error("Error fetching categories:\n%s", traceback.format_exc())
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch categories. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )


    @http.route('/products/category/<string:category_name>', type='http', auth='public', methods=['GET'], cors='*')
    def get_products_by_category(self, category_name):
        try:
            # Search public category by name
            category = request.env['product.public.category'].sudo().search([('name', '=', category_name)], limit=1)

            if not category:
                return request.make_response(
                    json.dumps({'status': False, 'message': f'Category "{category_name}" not found.'}),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )

            # Fetch products in the category
            products = request.env['product.template'].sudo().search([
                ('public_categ_ids', 'in', category.id),
                ('active', '=', True)
            ])

            product_list = [{
                'id': p.id,
                'name': p.name,
                'description': p.description or '',
                'list_price': p.list_price,
                'compare to price': p.compare_list_price or 0.0,
                'material_id': p.material_id.name if p.material_id else '',  # Material
                'care_guide_id': p.care_guide_id.name if p.care_guide_id else '',  # Care guide
                'items_included_id': p.items_included_id.name if p.items_included_id else '',  # Care guide
                'product_note_id': p.product_note_id or '',
                'is_published': p.is_published,
                'tags': [tag.name for tag in p.product_tag_ids] if p.product_tag_ids else [],  # 👈 Here you get tags
                'default_code': p.default_code or '',
                'on_hand_qty': p.qty_available or 0.0,
                'uom_id': p.uom_id.name if p.uom_id else '',
                'categ_id': p.categ_id.name if p.categ_id else '',
                'image_url': f"/web/image/product.template/{p.id}/image_1920" if p.image_1920 else '',
                'additional_media': [{
                    'id': img.id,
                    'name': img.name,
                    'image_url': f"/web/image/product.image/{img.id}/image_1920" if img.image_1920 else '',
                    'video_url': img.video_url or '',
                } for img in request.env['product.image'].sudo().search([
                    ('product_tmpl_id', '=', p.id),
                    ('image_1920', '!=', p.image_1920)  # Filter out duplicate of main image
                ])],
                'attributes': [
                    {
                        'id': attr.id,
                        'name': attr.name,
                        'values': [
                            {
                                'id': val.id,
                                'name': val.name
                            }
                            for val in p.product_variant_ids.mapped('product_template_attribute_value_ids')
                            .filtered(lambda x: x.attribute_id.id == attr.id)
                        ]
                    }
                    for attr in p.product_variant_ids.mapped('product_template_attribute_value_ids.attribute_id')
                ],
                'customer_reviews': [{
                    'name': review.partner_id.name if review.partner_id else '',
                    'rating': review.rating or 0.0,
                    'date': review.create_date.strftime('%Y-%m-%d') if review.create_date else '',
                    'review': review.feedback or ''
                } for review in request.env['rating.rating'].sudo().search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', p.id),
                    ('rating', '!=', 0),
                ])],

            } for p in products]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': f'Products in "{category_name}" category fetched successfully',
                    'data': product_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            import traceback
            _logger.error("Error fetching products by category:\n%s", traceback.format_exc())
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch products. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )

class ProductByTagController(http.Controller):

    @http.route('/products/tags', type='http', auth='public', methods=['GET'], cors='*')
    def get_all_product_tags(self):
        try:
            tags = request.env['product.tag'].sudo().search([])

            tag_list = [{
                'id': tag.id,
                'name': tag.name
            } for tag in tags]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'Product tags fetched successfully',
                    'data': tag_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            _logger.error("Error fetching product tags: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch tags. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )


    @http.route('/products/tags/<string:tag_name>', type='http', auth='public', methods=['GET'], cors='*')
    def get_products_by_tag(self, tag_name):
        try:
            # Search tag by name
            tag = request.env['product.tag'].sudo().search([('name', '=', tag_name)], limit=1)

            if not tag:
                return request.make_response(
                    json.dumps({'status': False, 'message': f'Tag "{tag_name}" not found.'}),
                    headers={'Content-Type': 'application/json'},
                    status=404
                )

            # Search for products with this tag
            products = request.env['product.template'].sudo().search([
                ('product_tag_ids', 'in', tag.id),
                ('active', '=', True)
            ])

            product_list = [{
                'id': p.id,
                'name': p.name,
                'description': p.description or '',
                'list_price': p.list_price,
                'compare to price': p.compare_list_price or 0.0,
                'default_code': p.default_code or '',
                'uom_id': p.uom_id.name if p.uom_id else '',
                'categ_id': p.categ_id.name if p.categ_id else '',
                'on_hand_qty': p.qty_available or 0.0,
                'is_published': p.is_published,
                'material_id': p.material_id.name if p.material_id else '',  # Material
                'care_guide_id': p.care_guide_id.name if p.care_guide_id else '',  # Care guide
                'items_included_id': p.items_included_id.name if p.items_included_id else '',  # Care guide
                'tags': [t.name for t in p.product_tag_ids],
                'image_url': f"/web/image/product.template/{p.id}/image_1920" if p.image_1920 else '',
                'additional_media': [{
                    'id': img.id,
                    'name': img.name,
                    'image_url': f"/web/image/product.image/{img.id}/image_1920" if img.image_1920 else '',
                    'video_url': img.video_url or '',
                } for img in request.env['product.image'].sudo().search([
                    ('product_tmpl_id', '=', p.id),
                    ('image_1920', '!=', p.image_1920)
                ])],# Filter out duplicate of main image
                'attributes': [
                    {
                        'id': attr.id,
                        'name': attr.name,
                        'values': [
                            {
                                'id': val.id,
                                'name': val.name
                            }
                            for val in p.product_variant_ids.mapped('product_template_attribute_value_ids')
                            .filtered(lambda x: x.attribute_id.id == attr.id)
                        ]
                    }
                    for attr in p.product_variant_ids.mapped('product_template_attribute_value_ids.attribute_id')
                ],
                'customer_reviews': [{
                    'name': review.partner_id.name if review.partner_id else '',
                    'rating': review.rating or 0.0,
                    'date': review.create_date.strftime('%Y-%m-%d') if review.create_date else '',
                    'review': review.feedback or ''
                } for review in request.env['rating.rating'].sudo().search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', p.id),
                    ('rating', '!=', 0),
                ])],
            } for p in products]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': f'Products with tag "{tag_name}" fetched successfully',
                    'data': product_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            import traceback
            _logger.error("Error fetching products by tag:\n%s", traceback.format_exc())
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch products. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )


_logger = logging.getLogger(__name__)


class ProductAttributeController(http.Controller):

    @http.route('/products/attributes', type='http', auth='public', methods=['GET'], cors='*')
    def get_product_attributes(self):
        try:
            attributes = request.env['product.attribute'].sudo().search([])

            attribute_list = []
            for attr in attributes:
                values = [{
                    'id': val.id,
                    'name': val.name
                } for val in attr.value_ids]

                attribute_list.append({
                    'id': attr.id,
                    'name': attr.name,
                    'values': values
                })

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'Product attributes fetched successfully',
                    'data': attribute_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            _logger.error("Error fetching product attributes: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch product attributes. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )


_logger = logging.getLogger(__name__)

class ProductVariantController(http.Controller):

    @http.route('/products/variant/list', type='http', auth='public', methods=['GET'], cors='*')
    def get_variant_id_and_name(self):
        try:
            variants = request.env['product.product'].sudo().search([])

            variant_list = [{
                'id': v.id,
                'name': v.name
            } for v in variants]

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'Product variant IDs and names fetched successfully.',
                    'data': variant_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            _logger.error("Error fetching variant IDs and names: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch variant list. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )


    @http.route('/products/variant', type='http', auth='public', methods=['GET'], cors='*')
    def get_product_variants(self):
        try:
            variants = request.env['product.product'].sudo().search([])

            variant_list = []
            for var in variants:
                attribute_values = [{
                    'attribute_name': val.attribute_id.name,
                    'value_name': val.name
                } for val in var.product_template_attribute_value_ids.mapped('product_attribute_value_id')]

                variant_list.append({
                    'variant_id': var.id,
                    'product_template_id': var.product_tmpl_id.id,
                    'product_template_name': var.product_tmpl_id.name,
                    'default_code': var.default_code,
                    'barcode': var.barcode,
                    'price': var.lst_price,
                    'attributes': attribute_values
                })

            return request.make_response(
                json.dumps({
                    'status': True,
                    'message': 'Product variants fetched successfully',
                    'data': variant_list
                }),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            _logger.error("Error fetching product variants: %s", str(e))
            return request.make_response(
                json.dumps({
                    'status': False,
                    'message': 'Unable to fetch product variants. Please try again later.'
                }),
                headers={'Content-Type': 'application/json'},
                status=500
            )
