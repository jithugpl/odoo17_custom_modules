from odoo import models, fields
from datetime import datetime, timedelta
import secrets

class ResUsers(models.Model):
    _inherit = 'res.users'

    auth_token = fields.Char("Auth Token")
    auth_token_expiry = fields.Datetime("Auth Token Expiry")

    def _generate_token(self):
        """Generate a secure token with a 24-hour expiry."""
        token = secrets.token_hex(32)
        expiry = datetime.now() + timedelta(hours=24)  # Token expires in 24 hours
        self.sudo().write({
            'auth_token': token,
            'auth_token_expiry': expiry,
        })
        return token