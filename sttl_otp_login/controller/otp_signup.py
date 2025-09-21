import re
from random import choice
import string
import logging
import werkzeug
from werkzeug.urls import url_encode
from odoo import http, tools, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.home import ensure_db, Home, SIGN_UP_REQUEST_PARAMS, LOGIN_SUCCESSFUL_PARAMS
from odoo.addons.base_setup.controllers.main import BaseSetup
from odoo.http import request
from odoo.exceptions import UserError
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)

LOGIN_SUCCESSFUL_PARAMS.add('account_created')


class OtpSignupHome(Home):

    @http.route(website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        q = request.params.copy()
        user_login = q.get('login')

        # Fetch OTP record using email (or login) to retrieve the phone number
        otp_record = request.env['otp.verification'].sudo().search([('email', '=', user_login)])

        if otp_record:
            phone_number = otp_record.phone

        else:
            phone_number = q.get('phone')  # If no OTP record, fallback to phone number in the request

        # After user creation, add phone number to the corresponding res.partner record
        user_login = qcontext.get('login')

        # phone_number = qcontext.get('phone')

        if user_login and otp_record.phone:
            print(user_login)
            user = request.env['res.users'].sudo().search([('login', '=', user_login)], limit=1)

            if user:
                # Check if partner exists for the user, or create one
                partner = user.partner_id
                if partner:
                    partner.sudo().write({'phone': phone_number})
                else:
                    # In case no partner is associated with the user, create a new partner
                    request.env['res.partner'].sudo().create({
                        'name': user.name,
                        'user_id': user.id,
                        'phone': phone_number,
                    })

                # Call the original signup method to create the user
        res = super(OtpSignupHome, self).web_auth_signup(*args, **kw)
        return res

    @http.route('/web/signup/otp', type='http', auth='public', website=True, sitemap=False)
    def web_signup_otp(self, **kw):

        qcontext = request.params.copy()
        print("qcontext : ",qcontext)
        user_name = str(qcontext.get('name'))
        print(user_name)

        # google captcha starting



        # google captcha ending


        #user_name is adding
        name_pattern = r"^(?=.*[a-zA-Z])(?=.{2,50}$)[a-z0-9]*[A-Z]?[a-z0-9]*(?:\s+[a-z0-9]*[A-Z]?[a-z0-9]*)*$"


        if not re.match(name_pattern, user_name):
            qcontext["error"] = _("Letters and numbers only, only 1 uppercase per word.")
            _logger.error(f"qcontext data: {qcontext}")
            response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
            return response

        # Validate phone number
        phone = qcontext.get('phone')
        if not phone:
            qcontext["error"] = _("Phone number is required.")
            response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
            return response

        OTP = self.generate_otp(4)

        if "login" in qcontext and qcontext["login"] and qcontext["password"] == qcontext["confirm_password"]:
            user_id = request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))])
            ph_id = request.env["res.partner"].sudo().search([("phone", "=", qcontext.get("phone"))])
            if user_id:
                qcontext["error"] = _("Another user is already registered using this email address.")
                response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
                return response
            if ph_id:
                qcontext["error"] = _("Another user is already registered using this phone number.")
                response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
                return response
            else:
                email = str(qcontext.get('login'))

                name = str(qcontext.get('name'))

                phone = str(qcontext.get('phone'))
                vals = {
                    'otp': OTP,
                    'email': email,
                    'phone': phone,
                }
                email_from = request.env.company.email
                mail_body = """\
                                <html>
                                    <body>
                                        <p>
                                            Dear <b>%s</b>,
                                                <br>
                                                <p>
                                                
                                                Your OTP for Carollia registration is {OTP}. It is valid for 10 minutes. Do not share it with anyone
                                                
                                                     <b>%s</b>
                                                </p>
                                            Thanks & Regards.
                                        </p>
                                    </body>
                                </html>
                            """ % (name, OTP)
                mail = request.env['mail.mail'].sudo().create({
                    'subject': _('Verify Your https://carollia.com/ Account - OTP Required'),
                    'email_from': email_from,
                    'email_to': email,
                    'body_html': mail_body,
                })

                mail.send()
                # Send OTP via SMS
                try:
                    sms_url = "https://prutech.org/SMS/api/broadcast"
                    auth_url = "https://prutech.org/SMS/api/token"
                    auth_payload = {
                        "username": "rajesh@datavalley.in",
                        "password": "wWPe%VOO*V^?*Zh"
                    }

                    auth_response = requests.post(auth_url, json=auth_payload)


                    if auth_response.status_code == 200:
                        token = auth_response.json().get("token")

                        sms_headers = {
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                        }

                        sms_payload = {
                            "pingBackType": "0",
                            "pingBackId": "0",
                            "jsonData": {
                                "senderId": "CARLIA",
                                "templateId": "1107173563435236694",
                                "templateName": "carollia user registration (www.carollia.com)",
                                "unicodeStatus": 0,
                                "messages": [
                                    {
                                        "msisdn": phone,  # Mobile number to send SMS
                                        "message": f"Your OTP for Carollia registration is {OTP}. It is valid for 10 minutes. Do not share it with anyone",
                                    }
                                ]
                            }
                        }


                        sms_response = requests.post(sms_url, headers=sms_headers, json=sms_payload)

                        if sms_response.status_code == 200:
                            sms_result = sms_response.json()
                            _logger.info("SMS Response -> %s", sms_result)
                            _logger.info("OTP sent successfully to %s", phone)

                        else:
                            _logger.error("Failed to send OTP to %s: %s", phone, sms_response.text)
                    else:
                        _logger.error("Failed to authenticate with SMS gateway: %s", auth_response.text)
                except Exception as e:
                    _logger.error("Error while sending OTP via SMS: %s", str(e))

                response = request.render('sttl_otp_login.custom_otp_signup', {'otp': True, 'otp_login': True,
                                                                               'login': qcontext["login"],
                                                                               'otp_no': OTP,
                                                                               'name': qcontext["name"],
                                                                               'password': qcontext["password"],
                                                                               'confirm_password': qcontext[
                                                                                   "confirm_password"],
                                                                               'phone': phone, })

                res = request.env['otp.verification'].sudo().create(vals)
                return response
        else:
            qcontext["error"] = _("Passwords do not match, please retype them.")
            response = request.render('sttl_otp_login.custom_otp_signup', qcontext)
            return response

    @http.route('/web/signup/otp/verify', type='http', auth='public', website=True, sitemap=False)
    def web_otp_signup_verify(self, *args, **kw):
        qcontext = request.params.copy()
        email = str(kw.get('login'))

        res_id = request.env['otp.verification'].search([('email', '=', email)], order="create_date desc", limit=1)

        name = str(kw.get('name'))
        password = str(qcontext.get('password'))
        confirm_password = str(qcontext.get('confirm_password'))

        try:

            current_time = datetime.now()  # Get the current system time
            time_difference = current_time - res_id.create_date

            _logger.warning("OTP check: Record %s created at %s; current time: %s; time difference: %s seconds",
                            res_id.id, res_id.create_date, current_time, time_difference.total_seconds())

            if time_difference.total_seconds() > 30:  # Check if more than 30 seconds
                _logger.warning("OTP Expired for record %s (time difference: %s seconds)",
                                res_id.id, time_difference.total_seconds())
                return request.render('sttl_otp_login.custom_login_template', {
                    'otp': True,
                    'otp_login': True,
                    'error_message': "OTP Expired. Please request a new OTP."
                })
            else:
                _logger.warning("Record %s: OTP is still valid. Created at %s",
                                res_id.id, res_id.create_date)



            otp = str(kw.get('otp'))
            otp_no = res_id.otp
            if otp_no == otp:
                res_id.state = 'verified'
                return self.web_auth_signup(*args, **kw)
            else:
                res_id.state = 'rejected'
                response = request.render('sttl_otp_login.custom_otp_signup', {'otp': True, 'otp_login': True,
                                                                               'login': email, 'name': name,
                                                                               'password': password,
                                                                               'confirm_password': confirm_password})
                return response
        except UserError as e:
            qcontext['error'] = e.name or e.value

        response = request.render('sttl_otp_login.custom_otp_signup', {'otp': True, 'otp_login': True,
                                                                       'login': email, 'name': name,
                                                                       'password': password,
                                                                       'confirm_password': confirm_password
                                                                       })
        return response

    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        return otp

    @http.route('/web/signup', type='http', auth='public', website=True, sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                # Send an account creation confirmation email
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(qcontext.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created',
                                           raise_if_not_found=False)
                if user_sudo and template:
                    res_id = request.env['otp.verification'].search([('email', '=', user_sudo.email)],
                                                                    order="create_date desc",
                                                                    limit=1)
                    user_sudo.partner_id.phone = res_id.phone
                    template.sudo().send_mail(user_sudo.id, force_send=True)
                return self.web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.args[0]
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.warning("%s", e)
                    qcontext['error'] = _("Could not create a new account.") + "\n" + str(e)

        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search(
                [('email', '=', qcontext.get('signup_email')), ('state', '!=', 'new')], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode({'login': user.login, 'redirect': '/web'}))

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response


