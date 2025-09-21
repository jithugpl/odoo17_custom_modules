from odoo import models, api, _
import requests
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    print("outside : _inherit = stock.picking def button_validate(self):")
    def button_validate(self):
        # Call the super method to process the picking
        print("inside : _inherit = stock.picking def button_validate(self):")
        result = super(StockPicking, self).button_validate()
        auth_url = "https://prutech.org/SMS/api/token"
        sms_url = "https://prutech.org/SMS/api/broadcast"

        # Check if this is a delivery order
        if self.picking_type_id.code == 'outgoing':
            # Get the customer's phone number and name
            customer_phone = self.partner_id.phone
            customer_name = self.partner_id.name
            print("customer_phone",customer_phone)
            print("customer_name",customer_name)

            # if not customer_phone:
            #     _logger.warning("Customer phone number is missing. SMS will not be sent.")
            #     return result

            # SMS API details
            auth_url = "https://prutech.org/SMS/api/token"
            sms_url = "https://prutech.org/SMS/api/broadcast"

            auth_payload = {
                "username": "rajesh@datavalley.in",
                "password": "wWPe%VOO*V^?*Zh"
            }



            print("auth_payload",auth_payload)

        try:
            # Authenticate and get token
            auth_response = requests.post(auth_url, json=auth_payload)
            print("auth_response:",auth_response)
            if auth_response.status_code == 200:
                token = auth_response.json().get("token")
                print("token",token)
                _logger.info("Authentication successful. Token received: %s", token)

                # Prepare SMS headers and payload
                sms_headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                }
                print("sms_headers",sms_headers)
                sms_payload = {
                    "pingBackType": "0",
                    "pingBackId": "0",
                    "jsonData": {
                        "senderId": "DVALEY",
                        "templateId": "1107173391262662673",
                        "templateName": "community connect password reset",
                        "unicodeStatus": 0,
                        "messages": [
                            {
                                "msisdn": str(9074627436),
                                "message": f"Dear {customer_name}, your OTP for resetting your password on the Community is 123456. This OTP is valid for 10 minutes. Please do not share it with anyone. -Data Valley Web Services",
                                "customerReferenceId": str(self.id)
                            }
                        ]
                    },
                    "validationFlag": "1",
                    "validatyPeriod": "",
                    "data": ""
                }

                print("sms_payload",sms_payload)
                print("sms_url",sms_url)

                # Send SMS
                sms_response = requests.post(sms_url, json=sms_payload, headers=sms_headers)
                print("sms_response.status_code:",sms_response.status_code) #this line  make issue odoo.addons.custom_sms_integration.models.sms_delivery_picking: Failed to send SMS. Status: 400, Response:

                if sms_response.status_code == 200:  #
                    sms_result = sms_response.json()
                    _logger.info("SMS sent successfully: %s", sms_result)
                else:
                    _logger.error("Failed to send SMS. Status: %d, Response: %s", sms_response.status_code,
                                  sms_response.text)
            else:
                _logger.error("Authentication failed. Status: %d, Response: %s", auth_response.status_code,
                              auth_response.text)
        except Exception as e:
            _logger.error("An error occurred while sending SMS: %s", str(e))

        return result

# # from addons.stock.populate.stock import Picking
# # from addons.stock.models.stock_picking import Picking
# from odoo import models, api, _
# import requests
# import logging
#
# _logger = logging.getLogger(__name__)
#
# class StockPicking(models.Model):
#     _inherit = "stock.picking"
#
#     print("outside : _inherit = stock.picking def action_done(self):")
#     def action_done(self):
#         print(" _inherit = stock.picking def action_done(self):")
#         # Call the super method to process the delivery
#         print("picking_type_id :",self.picking_type_id)
#         print("picking_type_id.code",self.picking_type_id.code)
#         result = super(Picking, self).action_done()
#
#         # Check if this is a delivery order
#         if self.picking_type_id.code == 'outgoing':
#             # Get the customer's phone number and name
#             customer_phone = self.partner_id.phone
#             print("customer_phone",customer_phone)
#             customer_name = self.partner_id.name
#             print("customer_name",customer_name)
#             if not customer_phone:
#                 _logger.warning("Customer phone number is missing. SMS will not be sent.")
#                 return result
#
#             # SMS API details
#             auth_url = "https://prutech.org/SMS/api/token "
#             sms_url = "https://prutech.org/SMS/api/broadcast"
#             auth_payload = {
#                 "username": "rajesh@datavalley.in",
#                 "password": "wWPe%VOO*V^?*Zh"
#             }
#             print("auth_payload",auth_payload)
#
#
#             try:
#                 # Authenticate and get token
#                 auth_response = requests.post(auth_url, json=auth_payload)
#                 print(auth_response)
#                 if auth_response.status_code == 200:
#                     token = auth_response.json().get("token")
#                     _logger.info("Authentication successful. Token received: %s", token)
#
#                     # Prepare SMS headers and payload
#                     sms_headers = {
#                         "Authorization": f"Bearer {token}",
#                         "Content-Type": "application/json",
#                     }
#                     print("sms_headers",sms_headers)
#                     sms_payload = {
#                         "pingBackType": "0",
#                         "pingBackId": "0",
#                         "jsonData": {
#                             "senderId": "DVALEY",
#                             "templateId": "1107173391262662673",
#                             "templateName": "community connect password reset",
#                             "unicodeStatus": 0,
#                             "messages": [
#                                 {
#                                     "msisdn": customer_phone,  # Fetch the customer's phone number
#                                     "message": f"Dear {customer_name}, your OTP for resetting your password on the Community is 123456. This OTP is valid for 10 minutes. Please do not share it with anyone. -Data Valley Web Services",  # Include dynamic data
#                                     "customerReferenceId": str(self.id)  # Delivery order ID
#                                 }
#                             ]
#                         },
#
#                         "validationFlag": "1",
#                         "validatyPeriod": "",
#                         "data": ""
#                     }
#                     print("sms_payload",sms_payload)
#
#                     # Send SMS
#                     sms_response = requests.post(sms_url, json=sms_payload, headers=sms_headers)
#                     if sms_response.status_code == 200:
#                         sms_result = sms_response.json()
#                         _logger.info("SMS sent successfully: %s", sms_result)
#                     else:
#                         _logger.error("Failed to send SMS. Status: %d, Response: %s", sms_response.status_code, sms_response.text)
#                 else:
#                     _logger.error("Authentication failed. Status: %d, Response: %s", auth_response.status_code, auth_response.text)
#             except Exception as e:
#                 _logger.error("An error occurred while sending SMS: %s", str(e))
#
#         return result
