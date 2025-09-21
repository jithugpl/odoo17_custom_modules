import contextlib
import random
import re

from odoo.addons.auth_signup.models.res_partner import now
# from carollia_dev.addons.auth_signup.models.res_partner import now
from odoo import models, api, _
import logging
import requests
from odoo.exceptions import UserError
from odoo.http import request

_logger = logging.getLogger(__name__)


class CustomUser(models.Model):
    _inherit = 'res.users'
    print("outside : result = super(CustomUser, self)._action_reset_password()")

    # @api.multi
    def _action_reset_password(self):
        print("inside : result = super(CustomUser, self)._action_reset_password()")

        """ Inherited function to print the reset password link """
        if self.env.context.get('install_mode') or self.env.context.get('import_file'):
            return
        if self.filtered(lambda user: not user.active):
            raise UserError(_("You cannot perform this action on an archived user."))

        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        account_created_template = None
        if create_mode:
            account_created_template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            if account_created_template and account_created_template._name != 'mail.template':
                _logger.error("Wrong set password template %r", account_created_template)
                return

        email_values = {
            'email_cc': False,
            'auto_delete': True,
            'message_type': 'user_notification',
            'recipient_ids': [],
            'partner_ids': [],
            'scheduled_date': False,
        }

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.", user.name))
            email_values['email_to'] = user.email
            with contextlib.closing(self.env.cr.savepoint()):
                if account_created_template:
                    account_created_template.send_mail(
                        user.id, force_send=True,
                        raise_exception=True, email_values=email_values)
                else:
                    # Rendering the email template
                    body = self.env['mail.render.mixin']._render_template(
                        self.env.ref('auth_signup.reset_password_email'),
                        model='res.users', res_ids=user.ids,
                        engine='qweb_view', options={'post_process': True})[user.id]
                    print("body before body.replace(&amp;, &)", body)
                    body = body.replace("&amp;", "&")
                    print("body after body.replace(&amp;, &)", body)

                    # Extract and print the reset password link from the body
                    if body:
                        # Replace &amp; with &
                        body = body.replace("&amp;", "&")
                        # Look for the link in the body content, if it follows the standard Odoo structure
                        start_index = body.find("href=\"http")
                        end_index = body.find("\"", start_index + 6)
                        reset_link = body[start_index + 6:end_index] if start_index != -1 else "No link found"

                        _logger.info(f"Reset password link for user {user.login}: {reset_link}")
                        print(f"Reset password link for user {user.login}: {reset_link}")
                        updated_url = re.sub(r'&amp;', '&', reset_link)
                        print("&amp removed url :", updated_url)
                        request.session['reset_password_link'] = updated_url


                    else:
                        _logger.error("Failed to render reset password email body.")

                    # Now create and send the email
                    mail = self.env['mail.mail'].sudo().create({
                        'subject': _('Password reset'),
                        'email_from': user.company_id.email_formatted or user.email_formatted,
                        'body_html': body,
                        **email_values,
                    })
                    # mail.send() #commented mail
                    _logger.info("commented mail")
                    _logger.info(f"the user is : {user.company_id.email_formatted or user.email_formatted}")
                    for user in self:
                        print("user.email : ", user.email)
                        # Directly fetch the email from the user instance
                        email = user.email
                        print("email : ", email)

                        if not email:
                            raise UserError(_("Cannot send email: user %s has no email address.", user.name))

                        # Use the email value for sending the OTP or reset link
                        print(f"Email for user {user.name}: {email}")

                        # Example: Populate email_values dictionary with the fetched email
                        email_values['email_to'] = email
                        print("email_values : ", email_values)
                        # Generate OTP
                        otp = random.randint(1000, 9999)
                        print("OTP : ", otp)
                        request.session['otp'] = otp

                    # Compose the email body
                    mail_body = f"""
                               <html>
                                   <body>
                                       <p>
                                           Dear <b>Ram</b>,
                                           <br><br>
                                           Your One-Time Password (OTP) for verifying your account is: 
                                           <b>{otp}</b>
                                           <br><br>
                                           Please use this OTP to complete your verification process. It is valid for 10 minutes.
                                           <br><br>
                                           Thanks & Regards,
                                           <br>Team Carollia
                                       </p>
                                   </body>
                               </html>
                           """
                    print(mail_body)
                    print(self.user_id.company_id.email)
                    # Create the email
                    mail = request.env['mail.mail'].sudo().create({
                        'subject': _('Verify Your Carollia Account - OTP Required'),
                        'email_from': self.user_id.company_id.email or 'noreply@carollia.com',
                        'email_to': email,
                        'body_html': mail_body,
                    })

                    # Send the email
                    try:
                        mail.send()
                        print("mail sent")
                        print(" before  return ")
                        return {
                            'type': 'ir.actions.act_url',
                            'url': '/verify/otp',
                            'target': 'self',
                        }
                        print("return works")

                        # return f"OTP has been sent to {email}."
                    except Exception as e:
                        return f"Error sending email: {str(e)}"
            _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
            # SMS Sending Logic:
            # Find the user by email
