from odoo import models, fields


class ProductMaterial(models.Model):
    _name = 'product.material'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _description = 'Product Material'

    name = fields.Char(string="Material", required=True)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)



class CareGuide(models.Model):
    _name = 'care.guide'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Care Guide'

    name = fields.Char(string="Care Guide", required=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)


class ItemsIncluded(models.Model):
    _name = 'items.included'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Items Included'

    name = fields.Char(string="Item", required=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)


class ProductNote(models.Model):
    _name = 'product.note'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Product Note'

    name = fields.Char(string="Note Title", required=True)
    product_note_id = fields.Html(string="Product Note", required=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user, readonly=True)

