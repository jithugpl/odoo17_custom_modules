
from odoo import http
from odoo.exceptions import UserError
from odoo.http import request


from odoo.addons.auth_signup.models.res_users import SignupError

# from carollia_dev.addons.auth_signup.models.res_partner import now
from odoo import models, api, _
import logging
import requests
from odoo.exceptions import UserError
from odoo.http import request


import werkzeug.exceptions
from odoo import http
from odoo.http import request
# from odoo.addons.controllers.main import AuthSignupHome
# from odoo.addons.web.controllers.main import ensure_db
import logging

from odoo.tools._monkeypatches_urls import url_encode

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)

class CustomAuthSignup(AuthSignupHome):
    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):

        # Call the parent method first to ensure original functionality
        response = super(CustomAuthSignup, self).web_auth_reset_password(*args, **kw)
        # print(otp)

        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("Password reset instructions sent to your email")
            except UserError as e:
                qcontext['error'] = e.args[0]
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')],
                limit=1
            )
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        # If message exists, redirect to OTP verification
        if qcontext.get('message') == _("Password reset instructions sent to your email"):
            return request.redirect('/verify/otp')

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response


class OTPController(http.Controller):
    @http.route('/verify/otp', type='http', auth='public', website=True, csrf=False)
    def otp_input_page(self, **kwargs):
        # Render OTP input form
        print("inside the /verify/otp controller")
        return request.render('custom_sms_integration.otp_input_template', {})

    @http.route('/verify/otp/submit', type='http', auth='public', website=True, csrf=False)
    def otp_submit(self, **kwargs):
        otp = kwargs.get('otp')
        print(otp)
        session_otp = request.session.get('otp')  # Get OTP from the session
        reset_password_link = request.session.get('reset_password_link')  # Get the reset password link from the session

        print(f"Session OTP: {session_otp}")
        print(f"Entered OTP: {otp}")
        print(f"Reset Password Link: {reset_password_link}")

        if not otp or not otp.isdigit() or len(otp) != 4:
            return request.render(
                'custom_sms_integration.otp_input_template',
                {'error': "Invalid OTP. Please enter a 4-digit number."}
            )

        # Compare the entered OTP with the OTP stored in the session
        if str(otp) == str(session_otp):
            print(f"Received OTP: {otp} matches session OTP: {session_otp}")
            # Redirect the user to the reset password link
            return request.redirect(reset_password_link)  # This will open the reset password link in a new tab
        else:
            print(f"Received OTP: {otp} does not match session OTP: {session_otp}")
            return request.render(
                'custom_sms_integration.otp_input_template',
                {'error': "Invalid OTP. Please try again."}
            )

# class OTPController(http.Controller):
#     @http.route('/verify/otp', type='http', auth='public', website=True, csrf=False)
#     def otp_input_page(self, **kwargs):
#         # Render OTP input form
#         print("inside the /verify/otp controller")
#         return request.render('custom_sms_integration.otp_input_template', {})
#
#     @http.route('/verify/otp/submit', type='http', auth='public', website=True, csrf=False)
#     def otp_submit(self, **kwargs):
#         otp = kwargs.get('otp')
#         print(otp)
#         session_otp = request.session.get('otp')  # Get OTP from the session
#         reset_password_link=request.session.get('reset_password_link')
#
#         print(session_otp)
#
#         if not otp or not otp.isdigit() or len(otp) != 4:
#             return request.render(
#                 'custom_sms_integration.otp_input_template',
#                 {'error': "Invalid OTP. Please enter a 4-digit number."}
#             )
#
#         # Compare the entered OTP with the OTP stored in the session
#         if otp == session_otp:
#             print(f"Received OTP: {otp} matches session OTP: {session_otp}")
#             return request.render(
#                 'custom_sms_integration.otp_success_template',
#                 {'message': "OTP verified successfully!"}
#             )
#         else:
#             print(f"Received OTP: {otp} does not match session OTP: {session_otp}")
#             return request.render(
#                 'custom_sms_integration.otp_input_template',
#                 {'error': "Invalid OTP. Please try again."}
#             )

# class OTPController(http.Controller):
#     @http.route('/verify/otp', type='http', auth='public', website=True, csrf=False)
#     def otp_input_page(self, **kwargs):
#         # Render OTP input form
#         print("in side the /verify/otp controller ")
#         return request.render('custom_sms_integration.otp_input_template', {})
