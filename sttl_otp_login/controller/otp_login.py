import re
from random import choice
import string
from datetime import datetime
from odoo.addons.web.controllers.home import Home, ensure_db
from odoo import http, _
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request, _logger
import requests


class CustomLoginController(Home):

    @http.route('/web/login', type='http', auth='public', website=True)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':
            user_captcha = kw.get('custom_captcha', '').strip().upper()
            generated_captcha = kw.get('generated_captcha', '').strip().upper()

            if user_captcha != generated_captcha:
                qcontext = self.get_auth_signup_qcontext()  # Get necessary context
                qcontext.update({
                    'error': 'Incorrect CAPTCHA. Please try again.',
                    'login': kw.get('login', ''),
                    'redirect': redirect,
                })
                return request.render('web.login', qcontext)  # Pass full context

        return super(CustomLoginController, self).web_login(redirect, **kw)


class AuthSignup(http.Controller):

    @http.route('/web/signup', type='http', auth='public', methods=['POST'], website=True, csrf=True)
    def signup_otp(self, **post):
        user_captcha = post.get('custom_captcha', '').strip().upper()
        generated_captcha = post.get('generated_captcha', '').strip().upper()

        # Check CAPTCHA validation
        if user_captcha != generated_captcha:
            qcontext = {
                'error': 'Incorrect CAPTCHA. Please try again.',
                'login': post.get('login', ''),
            }
            return request.render('auth_signup.signup', qcontext)  # Ensure correct template name

        # If CAPTCHA is correct, proceed to OTP page
        return request.redirect('/web/signup/otp')


class OtpLoginHome(Home):

    @http.route(website=True)
    def web_login(self, redirect=None, **kw):
        providers = request.env['auth.oauth.provider'].sudo().search([])
        ensure_db()
        qcontext = request.params.copy()

        _logger.info(f"Redirect argument: {redirect}")

        _logger.info("Keyword arguments (kw):")

        for key, value in kw.items():
            _logger.info(f"{key}: {value}")

        # Print the qcontext dictionary
        _logger.info("qcontext dictionary:")

        for key, value in qcontext.items():
            _logger.info(f"{key}: {value}")

        # Fetch the res.users record for the given login if it exists
        if 'login' in kw:
            user_record = request.env['res.users'].sudo().search([('login', '=', kw['login'])], limit=1)
            if user_record:

                _logger.info(f"Replacing 'login' value in kw with the actual login from res.users: {user_record.login}")

                kw['login'] = user_record.login
            else:

                _logger.warning(f"No user found with login: {kw['login']}")

        if 'login' in kw:
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Define email regex pattern for email validation
            mobile_pattern = r'^\d{10}$'  # Define mobile number regex pattern for 10-digit numbers

            if re.match(email_pattern, kw['login']):
                # Login is an email, fetch the corresponding `res.partner` ID
                partner = request.env['res.partner'].sudo().search([('email', '=', kw['login'])], limit=1)
                if partner:

                    _logger.info(f"Email found in res.partner: {kw['login']}, Partner ID: {partner.id}")

                    # Fetch the corresponding `res.users` record
                    user_record = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                    if user_record:

                        _logger.info(
                            f"Replacing 'login' value in kw with the actual login from res.users: {user_record.login}")

                        kw['login'] = user_record.login
                    else:

                        _logger.warning(f"No user found for partner with email: {kw['login']}")

                else:

                    _logger.warning(f"No partner found with email: {kw['login']}")


            elif re.match(mobile_pattern, kw['login']):
                # Login is a phone number, fetch the corresponding `res.partner` ID
                partner = request.env['res.partner'].sudo().search([('phone', '=', kw['login'])], limit=1)
                if partner:

                    _logger.info(f"Phone number found in res.partner: {kw['login']}, Partner ID: {partner.id}")

                    # Fetch the corresponding `res.users` record
                    user_record = request.env['res.users'].sudo().search([('partner_id', '=', partner.id)], limit=1)
                    if user_record:

                        _logger.info(
                            f"Replacing 'login' value in kw with the actual login from res.users: {user_record.login}")

                        kw['login'] = user_record.login
                    else:

                        _logger.warning(f"No user found for partner with phone: {kw['login']}")

                else:
                    _logger.warning(f"No partner found with phone: {kw['login']}")
            else:
                # Login is neither an email nor a 10-digit phone number
                _logger.error(f"Invalid login format: {kw['login']}")

        if request.httprequest.method == 'GET':

            if "otp_login" and "otp" in kw:
                if kw["otp_login"] and kw["otp"]:
                    return request.render("sttl_otp_login.custom_login_template",
                                          {'otp': True, 'providers': providers, 'otp_login': True})
            if "otp_login" in kw:  # checks if the keyword "otp_login" exists in the dict "kw".
                if kw["otp_login"]:  # checks if the value of "otp_login" is true.
                    return request.render("sttl_otp_login.custom_login_template",
                                          {'otp_login': True, 'providers': providers, })

            else:
                return super(OtpLoginHome, self).web_login(redirect, **kw)
        else:
            if kw.get('login'):
                request.params['login'] = kw.get('login').strip()
            if kw.get('password'):
                request.params['password'] = kw.get('password').strip()
            return super(OtpLoginHome, self).web_login(redirect, **kw)

        return request.render("sttl_otp_login.custom_login_template", {'providers': providers, })

    @http.route('/web/otp/login', type='http', auth='public', website=True, csrf=False)
    def web_otp_login(self, **kw):
        qcontext = request.params.copy()
        email_or_phone = str(qcontext.get('login'))
        providers = request.env['auth.oauth.provider'].sudo().search([])

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Define email regex patter

        mobile_pattern = r'^\d{10}$'  # Define phone regex pattern (strictly 10 digits)
        if re.match(email_pattern, email_or_phone):

            user_id = request.env['res.partner'].sudo().search([('email', '=', email_or_phone)],
                                                               limit=1)  # If the input matches email regex
            # print("Email user_id",user_id.id)
            _logger.info(f"Email user_id: {user_id.id}")

            if not user_id:
                # If no user found, return an error message
                return request.render("sttl_otp_login.custom_login_template", {
                    'otp': False,
                    'otp_login': True,
                    'login_error': True,
                    'providers': providers,
                    'error_message': "The provided email address does not exist in our records."
                })

        elif re.match(mobile_pattern, email_or_phone):

            user_id = request.env['res.partner'].sudo().search([('phone', '=', email_or_phone)],
                                                               limit=1)  # If the input matches phone number regex (10 digits)

            _logger.info(f"Phone user_id: {user_id.id}")

            if not user_id:
                # If no user found, return an error message
                return request.render("sttl_otp_login.custom_login_template", {
                    'otp': False,
                    'otp_login': True,
                    'login_error': True,
                    'providers': providers,
                    'error_message': "The provided phone number does not exist in our records."
                })
        else:

            user_id = None  # If it's neither email nor phone number, user_id remains None
            _logger.warning("No user_id found (None).")
            # If the input is neither email nor phone, show an invalid format error
            _logger.warning("Invalid input format: The provided input is neither an email nor a 10-digit phone number.")

            return request.render("sttl_otp_login.custom_login_template", {
                'otp': False,
                'otp_login': True,
                'login_error': True,
                'providers': providers,
                # 'error_message': "Invalid email or phone number format. Please enter a valid email address or a 10-digit phone number."
            })

        # user_id = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1) #fetch the corresponding res.partner based on the email
        _logger.info(f"user_id: {user_id.id}")
        providers = request.env['auth.oauth.provider'].sudo().search([])

        _logger.info(f"user_id.id: {user_id.id}")

        user_id = request.env['res.users'].sudo().search([('partner_id', '=', user_id.id)], limit=1)
        if user_id:

            OTP = self.generate_otp(4)

            # Check if the input is a valid email
            if re.match(email_pattern, email_or_phone):
                # It's an email, so assign it to the email field
                vals = {
                    'otp': OTP,
                    'email': email_or_phone,
                    'phone': ""  # No phone number
                }

            elif re.match(mobile_pattern, email_or_phone):  # Check if the input is a phone number (exactly 10 digits)
                # It's a phone number, so assign it to the phone field
                vals = {
                    'otp': OTP,
                    'email': "",
                    'phone': email_or_phone
                }

            else:
                # Invalid input, no email or phone
                vals = {
                    'otp': "",
                    'email': "",
                    'phone': ""
                }

            # vals = {
            #     'otp': OTP,
            #     'email': email_or_phone,
            # }
            mail_body = """\
                                    <html>
                                        <body>
                                            <p>
                                                Dear <b>%s</b>,
                                                    <br>
                                                    <p> 
                                                    Your OTP for logging into Carollia is {OTP}. Valid for 10 minutes. Do not share it with anyone
                                                        <b>%s</b>
                                                    </p>
                                                Thanks & Regards.
                                            </p>
                                        </body>
                                    </html>
                                """ % (user_id.name, OTP)

            _logger.info(f"user_id.partner_id.email: {user_id.partner_id.email}")

            mail = request.env['mail.mail'].sudo().create({
                'subject': _('Verify Your carollia.com Account - OTP Required'),
                'email_from': user_id.company_id.email,
                'author_id': user_id.partner_id.id,
                'email_to': user_id.partner_id.email,
                'body_html': mail_body,
            })

            _logger.info(f"user_id.user_id.id: {user_id.user_id.id}")
            _logger.info(f"user_id.company_id: {user_id.company_id}")
            _logger.info(f"Mail object created: {mail}")
            mail.send()

            _logger.info(f"Phone number for SMS: {user_id.partner_id.phone}")

            if user_id.partner_id.phone:
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
                                "templateId": "1107173563469215746",
                                "templateName": "carollia OTP login (www.carollia.com)",
                                "unicodeStatus": 0,
                                "messages": [
                                    {
                                        "msisdn": user_id.partner_id.phone,  # Mobile number to send SMS
                                        "message": f"Your OTP for logging into Carollia is {OTP}. Valid for 10 minutes. Do not share it with anyone",
                                    }
                                ]
                            }
                        }
                        sms_response = requests.post(sms_url, headers=sms_headers, json=sms_payload)
                        _logger.info("SMS Response -> %s", sms_response)

                        _logger.info("sms_response.status_code: %s", sms_response.status_code)
                        if sms_response.status_code == 200:
                            _logger.info("sms_response.status_code: %s", sms_response.status_code)
                        else:
                            _logger.error("Failed to send OTP to %s: %s", user_id.partner_id.phone, sms_response.text)
                    else:
                        _logger.error("Failed to authenticate with SMS gateway: %s", auth_response.text)
                except Exception as e:
                    _logger.exception("Error while sending OTP via SMS: %s", e)

            # Send OTP via SMS
            # phone = user_id.partner_id.phone  # Assuming the phone number is stored in partner
            # print("phone ->", phone)

            response = request.render("sttl_otp_login.custom_login_template", {'otp': True, 'otp_login': True,
                                                                               'providers': providers,
                                                                               'login': qcontext["login"],
                                                                               'otp_no': OTP})
            request.env['otp.verification'].sudo().create(vals)
            return response

        else:
            response = request.render("sttl_otp_login.custom_login_template", {'otp': False, 'otp_login': True,
                                                                               'providers': providers,
                                                                               'login_error': True})
        return response

    @http.route('/web/otp/verify', type='http', auth='public', website=True, csrf=False)
    def web_otp_verify(self, *args, **kw):
        providers = request.env['auth.oauth.provider'].sudo().search([])
        qcontext = request.params.copy()
        email_or_phone = str(kw.get('login'))

        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'  # Define email regex patter

        mobile_pattern = r'^\d{10}$'  # Define phone regex pattern (strictly 10 digits)
        _logger.info("Received email or phone: %s", email_or_phone)

        if re.match(email_pattern, email_or_phone):
            res_id = request.env['otp.verification'].search([('email', '=', email_or_phone)], order="create_date desc",
                                                            limit=1)  # If the input matches email regex

            _logger.info(f"Email-based OTP record ID: {res_id.id}")

            if not res_id or res_id is None:
                return request.render('sttl_otp_login.custom_login_template', {
                    'otp': False,
                    'otp_login': True,
                    'login_error': True,
                    'providers': providers,
                    'error_message': "No OTP record found. Please check your email/phone and try again."
                })

            user_id = request.env['res.partner'].sudo().search([('email', '=', email_or_phone)], limit=1)

            _logger.info(f"Partner ID for email: {user_id.id}")

            user_id = request.env['res.users'].sudo().search([('partner_id', '=', user_id.id)], limit=1)

            _logger.info(f"User ID for email: {user_id.id}")

        elif re.match(mobile_pattern, email_or_phone):
            res_id = request.env['otp.verification'].sudo().search([('phone', '=', email_or_phone)],
                                                                   order="create_date desc",
                                                                   limit=1)  # If the input matches phone number regex (10 digits)
            _logger.info(f"Phone-based OTP record ID: {res_id.id}")
            user_id = request.env['res.partner'].sudo().search([('phone', '=', email_or_phone)], limit=1)
            _logger.info(f"Partner ID for phone: {user_id.id}")
            user_id = request.env['res.users'].sudo().search([('partner_id', '=', user_id.id)], limit=1)
            _logger.info(f"User ID for phone: {user_id.id}")
        else:

            res_id = None  # If it's neither email nor phone number, user_id remains None
            _logger.warning(f"No matching record found for input: {email_or_phone}")
        # res_id = request.env['otp.verification'].search([('email', '=', email)], order="create_date desc", limit=1)

        otp_verification_records = request.env['otp.verification'].sudo().search([], order='create_date desc',
                                                                                 limit=2)  # Fetch all records from the otp.verification model
        # Print all fields of the records
        
        for record in otp_verification_records:
                _logger.debug(
                    f"OTP: {record.otp} | State: {record.state} | Email: {record.email} | Phone: {record.phone}"
                )
                print("---")

        try:

            current_time = datetime.now()  # Get the current system time
            time_difference = current_time - res_id.create_date
            _logger.warning("OTP check: Record %s created at %s; current time: %s; time difference: %s seconds",
                            res_id.id, res_id.create_date, current_time, time_difference.total_seconds())

            if time_difference.total_seconds() > 30:  # Check if more than 1 minute
                _logger.warning("OTP Expired for record %s (time difference: %s seconds)",
                                res_id.id, time_difference.total_seconds())
                return request.render('sttl_otp_login.custom_login_template', {
                    'otp': True,
                    'otp_login': True,
                    'providers': providers,
                    # 'login': user_id.login,
                    'error_message': "OTP Expired. Please request a new OTP."
                })
            else:
                _logger.warning("Record %s: OTP is still valid. Created at %s",
                                res_id.id, res_id.create_date)    


            otp = str(kw.get('otp'))
            otp_no = res_id.otp
            if otp_no == otp:
                res_id.state = 'verified'

                _logger.info(f"Verified OTP for user_id: {user_id.id}, OTP: {otp}")
                # user_id = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
                request.env.cr.execute(
                    "SELECT COALESCE(password, '') FROM res_users WHERE id=%s",
                    [user_id.id]
                )
                hashed = request.env.cr.fetchone()[0]
                qcontext.update({'login': user_id.sudo().login,
                                 'name': user_id.sudo().partner_id.name,
                                 'password': hashed + 'mobile_otp_login'})

                _logger.info("qcontext details:")

                for key, value in qcontext.items():
                    _logger.debug(f"{key}: {value}")
                _logger.debug("---")

                request.params.update(qcontext)
                _logger.info(f"State: {res_id.state}")
                return self.web_login(*args, **kw)
            else:
                res_id.state = 'rejected'
                _logger.warning(f"Login rejected for user: {user_id.login}")
                response = request.render('sttl_otp_login.custom_login_template', {'otp': True, 'otp_login': True,
                                                                                   'providers': providers,
                                                                                   'login': user_id.login})
                return response
        except UserError as e:
            _logger.error("An error occurred in OTP verification", exc_info=True)
            qcontext['error'] = e.name or e.value

        response = request.render('sttl_otp_login.custom_login_template', {'otp': True, 'otp_login': True,
                                                                           'providers': providers,
                                                                           'login': user_id.login})
        return response

    def generate_otp(self, number_of_digits):
        otp = ''.join(choice(string.digits) for _ in range(number_of_digits))
        _logger.info(f"Generated OTP: {otp}")
        return otp
