from odoo import models, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    print("outside : result = super(SaleOrder, self).action_confirm()")

    @api.model
    def action_confirm(self):
        print("inside : result = super(SaleOrder, self).action_confirm()")
        """
        Override the action_confirm method to include SMS sending functionality.
        """
        # Call the original action_confirm method
        result = super(SaleOrder, self).action_confirm()

        # SMS sending logic
        auth_url = "https://prutech.org/SMS/api/token"
        sms_url = "https://prutech.org/SMS/api/broadcast"

        auth_payload = {
            "username": "rajesh@datavalley.in",
            "password": "wWPe%VOO*V^?*Zh"
        }
        print("auth_payload", auth_payload)

        for order in self:
            try:
                # Authenticate and get token
                auth_response = requests.post(auth_url, json=auth_payload)
                print("auth_response.status_code",auth_response)
                if auth_response.status_code == 200:
                    token = auth_response.json().get("token")
                    if  token:
                         print("Authentication successful. Token received: %s", token)

                    # Prepare SMS headers and payload
                    sms_headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    }
                    print("phone number :",order.partner_id.phone)
                    print("order.partner_id.name :",order.partner_id.name)
                    print("order.id : ",order.id)
                    sms_payload = {
                        "pingBackType": "0",
                        "pingBackId": "0",
                        "jsonData": {
                            "senderId": "CARLIA",
                            "templateId": "1107173563544729836",
                            "templateName": "carollia shipment message (www.carollia.com)",
                            "unicodeStatus": 0,
                            "messages": [
                                {
                                    "msisdn": "9074627436",
                                    "message": "Your order #{#var#} from Carollia is on its way! Track your shipment: {#var#}.",
                                    "customerReferenceId": "12345"
                                }
                            ]
                        },
                        "validationFlag": "1",
                        "validatyPeriod": "",
                        "data": ""
                    }
                    print("sms_payload",sms_payload)
                    print('sms_headers',sms_headers)
                    print("sms_url",sms_url)
                    _logger.info("SMS Payload being sent: %s", sms_payload)


                    # Send SMS
                    sms_response = requests.post(sms_url, json=sms_payload, headers=sms_headers)
                    _logger.info("SMS Response: %s", sms_response.json())

                    print("sms_response.status_code : ",sms_response.status_code)
                    # _logger.info("SMS Response: %s", sms_response.json())
                    print("Message content:", sms_payload['jsonData']['messages'][0]['message'])
                    if sms_response.status_code == 200:
                        sms_result = sms_response.json()
                        if sms_result.get("status") != 1:  # Assuming `1` is success
                            _logger.error("SMS sending failed. Message: %s", sms_result.get("message"))
                            raise UserError(_("SMS sending failed: %s" % sms_result.get("message")))
                    else:
                        _logger.error("SMS service returned error. Status: %d, Response: %s",
                                      sms_response.status_code, sms_response.text)

                    # if sms_response.status_code == 200:
                    #     print(sms_response.json())
                    #     sms_result = sms_response.json()
                    #     _logger.info("SMS sent successfully for Sale Order %s: %s", order.name, sms_result)
                    # else:
                    #     _logger.error("Failed to send SMS for Sale Order %s. Status: %d, Response: %s",
                    #                   order.name, sms_response.status_code, sms_response.text)
                else:
                    _logger.error("Authentication failed for SMS service. Status: %d, Response: %s",
                                  auth_response.status_code, auth_response.text)
            except Exception as e:
                _logger.error("An error occurred while sending SMS for Sale Order %s: %s", order.name, str(e))

        return result





# from odoo import models, api, _
# import requests
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class SaleOrder(models.Model):
#     _inherit = "sale.order"
#
#     @api.model
#     def create(self, vals):
#         print("the sms class is works ")
#         # Call the super method to create the sales order
#         try:
#             sale_order = super(SaleOrder, self).create(vals)
#         except Exception as e:
#             _logger.error("Failed to create sale order: %s", str(e))
#             raise  # Re-raise the exception after logging
#
#         # Get the customer phone number
#         customer_phone = sale_order.partner_id.phone
#         if not customer_phone:
#             _logger.warning("Customer phone number is missing. SMS will not be sent.")
#             return sale_order
#
#         # SMS API URLs and payloads
#         auth_url = "https://prutech.org/SMS/api/token"
#         sms_url = "https://prutech.org/SMS/api/broadcast"
#
#         auth_payload = {
#             "username": "rajesh@datavalley.in",
#             "password": "wWPe%VOO*V^?*Zh"
#         }
#
#         try:
#             # Authenticate and get token
#             auth_response = requests.post(auth_url, json=auth_payload)
#             print(auth_response)
#             auth_response.raise_for_status()  # Raise an error for bad responses
#             print("auth_response",auth_response)
#
#             token = auth_response.json().get("token")
#             print("token",token)
#             if not token:
#                 _logger.error("Authentication successful but no token received.")
#                 return sale_order
#
#             _logger.info("Authentication successful. Token received: %s", token)
#
#             # Prepare SMS headers and payload
#             sms_headers = {
#                 "Authorization": f"Bearer {token}",
#                 "Content-Type": "application/json",
#             }
#             print("sms_headers",sms_headers)
#             print("sale_order.partner_id.phone",sale_order.partner_id.phone,"sale_order.name",sale_order.name,"sale_order.id",sale_order.id)
#             print("sms_payload")
#
#             sms_payload = {
#                 "pingBackType": "0",
#                 "pingBackId": "0",
#                 "jsonData": {
#                     "senderId": "DVALEY",
#                     "templateId": "1107173391262662673",
#                     "templateName": "community connect password reset",
#                     "unicodeStatus": 0,
#                     "messages": [
#                         {
#                             "msisdn":sale_order.partner_id.phone,
#                             "message": f"Dear{sale_order.partner_id.name}, your OTP for resetting your password on the Community is 123456. This OTP is valid for 10 minutes. Please do not share it with anyone. -Data Valley Web Services",
#                             "customerReferenceId": str(sale_order.id)
#                         }
#                     ]
#                 },
#                 "validationFlag": "1",
#                 "validatyPeriod": "",
#                 "data": ""
#             }
#             print("sms_payload")
#
#             # Send SMS
#             sms_response = requests.post(sms_url, json=sms_payload, headers=sms_headers)
#             sms_response.raise_for_status()  # Raise an error for bad responses
#
#             sms_result = sms_response.json()
#             _logger.info("SMS sent successfully: %s", sms_result)
#
#         except requests.exceptions.HTTPError as http_err:
#             print("HTTP error occurred: %s", str(http_err))
#             _logger.error("HTTP error occurred: %s", str(http_err))
#         except requests.exceptions.ConnectionError as conn_err:
#             print("Connection error occurred: %s", str(conn_err))
#             _logger.error("Connection error occurred: %s", str(conn_err))
#         except requests.exceptions.Timeout as timeout_err:
#             print("Timeout error occurred: %s", str(timeout_err))
#             _logger.error("Timeout error occurred: %s", str(timeout_err))
#         except requests.exceptions.RequestException as req_err:
#             print("Request exception occurred: %s", str(req_err))
#             _logger.error("Request exception occurred: %s", str(req_err))
#         except Exception as e:
#             print("An unexpected error occurred while sending SMS: %s", str(e))
#             _logger.error("An unexpected error occurred while sending SMS: %s", str(e))
#
#         return sale_order
