from odoo import models, api

class WebsiteReview(models.Model):
    _inherit = 'rating.rating'

    @api.model
    def create(self, vals):
        review = super(WebsiteReview, self).create(vals)
        if vals.get('attachment_ids'):
            # Ensure attachments are public for visibility
            attachment_ids = vals['attachment_ids'][0][2] if isinstance(vals['attachment_ids'], list) else vals['attachment_ids']
            self.env['ir.attachment'].browse(attachment_ids).write({'public': True})
        return review
