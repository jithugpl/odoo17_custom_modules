from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    price_total_amount_in_words = fields.Char(string='Amount In Words', compute='_compute_price_total_amount_in_words')

    @api.depends('amount_total')
    def _compute_price_total_amount_in_words(self):
        for move in self:
            if move.currency_id:
                currency = self.env['res.currency'].browse(move.currency_id.id)
                if currency:
                    move.price_total_amount_in_words = currency.amount_to_text(move.amount_total)
                else:
                    move.price_total_amount_in_words = False
            else:
                move.price_total_amount_in_words = False
