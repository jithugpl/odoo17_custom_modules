from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PackageTemplates(models.Model):
    _name = 'package.template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Package Template'
    _rec_name = 'product_id'
    _order = 'create_date desc'

    product_id = fields.Many2one('product.product', string='Product', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UOM',  related='product_id.uom_id', store=True, readonly=True,
                             precompute=True, required=True, tracking=True)
    state = fields.Selection([('review', 'Review'), ('confirm', 'Confirmed')], default='review', required=True,
                             readonly=True, index=True, string='State', tracking=True, store=True)
    package_template_line_ids = fields.One2many('package.template.line', 'package_template_id',
                                                string='Package Template Lines')
    company_id = fields.Many2one(comodel_name='res.company', required=True, index=True,
                                 default=lambda self: self.env.company)


    def action_confirm(self):
        for template in self:
            if not template.package_template_line_ids:
                raise UserError(
                    _('You cannot confirm a package template without any items. Please add at least one item.'))
            template.state = 'confirm'

    def back_to_review(self):
        self.state = 'review'


class PackageTemplateLine(models.Model):
    _name = 'package.template.line'
    _description = 'Package Template Line'

    product_id = fields.Many2one('product.product', string='Item',tracking=True)
    uom_id = fields.Many2one('uom.uom', string='UOM', compute='_compute_product_uom_unit', store=True,)
    quantity = fields.Float(string='Quantity', default=1,tracking=True)
    cost = fields.Float(string='Cost', compute='_compute_product_uom_unit')
    amount = fields.Float(string='Amount', compute='_compute_product_uom_unit')
    package_template_id = fields.Many2one('package.template', string='Package Template')
    name = fields.Char('Description', compute='_compute_description',store=True, readonly=False)
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
        ],
        default=False
    )


    @api.depends('product_id','quantity', 'cost')
    def _compute_product_uom_unit(self):
        for line in self:
            line.uom_id = line.product_id.uom_id
            line.cost = line.product_id.list_price
            line.amount = line.quantity * line.cost

    @api.depends('product_id')
    def _compute_description(self):
        for line in self:
            line.name = line.product_id.description_sale or line.product_id.name

class SaleOrderQuotation(models.Model):
    _inherit = 'sale.order'

    package_template_ids = fields.Many2many('package.template', string='Package Template')
    profit_percentage = fields.Float(string='Profit %', copy=False, tracking=True)
    net_cost = fields.Float(string='Total Cost', compute='_compute_net_cost', store=True)
    net_profit_amount = fields.Float(string='Total Profit', compute='_compute_net_cost', store=True)
    additional_details = fields.Char(string='Additional Details')
    extra_data = fields.Char(string="Add a note")
    total_discount_amount = fields.Float(string='Total Discount Amount', compute='_compute_total_discount_amount',
                                         store=True)

    @api.depends('order_line.disc_amount')
    def _compute_total_discount_amount(self):
        for order in self:
            order.total_discount_amount = sum(line.disc_amount for line in order.order_line)


    def action_profit_percentage(self):
        for order in self:
            for line in order.order_line:
                if line.product_id:
                    sales_price = line.cost
                    new_price = (sales_price * (order.profit_percentage / 100)) + sales_price
                    line.update({
                        'price_unit': new_price,
                        'profit': order.profit_percentage,
                    })
                    line._compute_cost()
            order._compute_net_cost()
        for option in order.sale_order_option_ids:
            if option.product_id:
                sales_price = option.cost
                new_price = (sales_price * (order.profit_percentage / 100)) + sales_price
                option.update({
                    'price_unit': new_price,
                    'profit': order.profit_percentage,
                })
                option._compute_cost()

    @api.depends('order_line.cost_amount')
    def _compute_net_cost(self):
        for order in self:
            order.net_cost = sum(order.order_line.mapped('cost_amount'))
            order.net_profit_amount = sum(order.order_line.mapped('profit_amount'))



    def action_generate_lines_from_packages(self):
        for order in self:
            # Get the existing product lines added manually
            existing_lines = order.order_line.filtered(lambda l: not l.package_template_line_id)

            # Unlink only the lines generated from package templates
            order.order_line.filtered(lambda l: l.package_template_line_id).unlink()

            for template in order.package_template_ids:
                if template.state != 'confirm':
                    raise UserError(
                        _('The package template %s is not confirmed. Please confirm it.') % template.product_id.display_name)

                for line in template.package_template_line_ids:
                    order.order_line.create({
                        'order_id': order.id,
                        'sequence': line.id,
                        'name': line.name,
                        'display_type': line.display_type,
                        'product_id': line.product_id.id,
                        'product_uom': line.uom_id.id,
                        'product_uom_qty': line.quantity,
                        'price_unit': line.cost,
                        'cost': line.cost,
                        'cost_amount': line.amount,
                        'package_template_line_id': line.id,  # Link to the package template line
                    })

            # Re-add the manually created product lines if they were unlinked
            if existing_lines:
                order.order_line = [(4, line.id) for line in existing_lines]


class SaleOrderLineQuotation(models.Model):
    _inherit = 'sale.order.line'

    profit = fields.Float(string='Profit %')
    cost = fields.Float(string='Cost', compute='_compute_cost', store=True)
    cost_amount = fields.Float(string='Cost Amount', compute='_compute_cost')
    profit_amount = fields.Float(string='Profit Amount', compute='_compute_cost')
    package_template_line_id = fields.Many2one('package.template.line', string='Package Template Line')
    additional_details = fields.Char(string='Additional Details')
    serial_number = fields.Integer(string="Sl No", compute='_get_line_numbers',readonly=False, default=False)
    disc_amount = fields.Float(string='Disc.Amount',compute='_compute_discount_amount')
    product_image = fields.Image(related='product_id.image_1920', string="Product Image", readonly=True)

    @api.depends('product_uom_qty','price_unit','discount')
    def _compute_discount_amount(self):
        for line in self:
            discount_amount = (line.product_uom_qty * line.price_unit * (line.discount / 100))
            line.disc_amount = discount_amount

    @api.depends('order_id.order_line')
    def _get_line_numbers(self):
        for line in self:
            no = 0
            line.serial_number = no
            for l in line.order_id.order_line:
                if l.display_type not in ('line_section', 'line_note'):
                    no += 1
                    l.serial_number = no


    @api.depends('product_id', 'product_uom_qty')
    def _compute_cost(self):
        for line in self:
            line.cost = line.product_id.list_price
            line.cost_amount = line.product_uom_qty * line.product_id.list_price
            line.profit_amount = (line.profit / 100) * line.cost_amount
            if line.product_id and line.profit:
                sales_price = line.product_id.list_price
                new_price = (sales_price * (line.profit / 100)) + sales_price
                line.price_unit = new_price
                line.profit_amount = (line.profit / 100) * line.cost_amount

    @api.onchange('profit')
    def _onchange_profit(self):
        for line in self:
                if line.product_id and line.profit:
                    sales_price = line.product_id.list_price
                    new_price = (sales_price * (line.profit / 100)) + sales_price
                    line.price_unit = new_price
                    line.profit_amount = (line.profit / 100) * line.cost_amount




class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    profit = fields.Float(string='Profit %')
    cost = fields.Float(string='Cost',compute='_compute_cost', store=True)
    cost_amount = fields.Float(string='Cost Amount',compute='_compute_cost')
    profit_amount = fields.Float(string='Profit Amount',compute='_compute_cost')
    tax_id = fields.Many2many('account.tax', string='Taxes',compute='_compute_tax_id')
    sl_no = fields.Integer(string="Sl No",
                           compute='_get_line_number'
                           )

    @api.depends('order_id.sale_order_option_ids')
    def _get_line_number(self):
        for line in self:
            no = 0
            line.sl_no = no
            for l in line.order_id.sale_order_option_ids:
                    no += 1
                    l.sl_no = no


    @api.depends('product_id')
    def _compute_tax_id(self):
        for line in self:
            if line.product_id:
                line.tax_id = [(6, 0, line.product_id.taxes_id.ids)]
            else:
                line.tax_id = [(5, 0, 0)]  # Clear taxes if no product is set

    @api.depends('product_id', 'quantity')
    def _compute_cost(self):
        for line in self:
            line.cost = line.product_id.list_price
            line.cost_amount = line.quantity * line.product_id.list_price
            line.profit_amount = (line.profit / 100) * line.cost_amount
            if line.product_id and line.profit:
                sales_price = line.product_id.list_price
                new_price = (sales_price * (line.profit / 100)) + sales_price
                line.price_unit = new_price
                line.profit_amount = (line.profit / 100) * line.cost_amount

    @api.onchange('profit')
    def _onchange_profit(self):
        for line in self:
            if line.product_id and line.profit:
                sales_price = line.product_id.list_price
                new_price = (sales_price * (line.profit / 100)) + sales_price
                line.price_unit = new_price
                line.profit_amount = (line.profit / 100) * line.cost_amount





