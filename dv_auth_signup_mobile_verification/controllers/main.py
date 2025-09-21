import logging
from odoo import _
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class MobileSignupController:
    @route('/auth/signup/mobile_check', type='http', auth='public', website=True, csrf=False)
    def check_mobile_signup(self, **kwargs):
        """Validate and handle mobile number during signup."""
        values = request.params
        qcontext = self.get_signup_qcontext()

        # Validate the mobile number
        mobile_number = values.get("mobile", "").strip()
        if not mobile_number:
            qcontext["error"] = _("Mobile number is required.")
            return request.render("auth_signup.signup", qcontext)

        # Check if the mobile number is valid
        if not mobile_number.isdigit() or len(mobile_number) != 10:
            qcontext["error"] = _("Please enter a valid 10-digit mobile number.")
            return request.render("auth_signup.signup", qcontext)

        # Check if the mobile number already exists
        existing_user = request.env['res.users'].sudo().search([('mobile', '=', mobile_number)], limit=1)
        if existing_user:
            qcontext["error"] = _("A user is already registered with this mobile number.")
            return request.render("auth_signup.signup", qcontext)

        # Return a success message or handle further logic
        qcontext["mobile"] = mobile_number
        qcontext["message"] = _("Mobile number is valid and can be used for signup.")
        return request.render("auth_signup.signup", qcontext)

    def get_signup_qcontext(self):
        """Helper method to fetch the signup context."""
        qcontext = dict(request.params)
        qcontext.update({
            'error': None,
            'message': None,
        })
        return qcontext
