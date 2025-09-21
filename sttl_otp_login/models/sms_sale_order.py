from odoo import models, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"
    _logger.info("outside: result = super(SaleOrder, self).action_confirm()")


    @api.model
    def action_confirm(self):
        _logger.info("inside: result = super(SaleOrder, self).action_confirm()")
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
        _logger.info("Auth Payload: %s", auth_payload)

        for order in self:
            try:
                # Authenticate and get token
                auth_response = requests.post(auth_url, json=auth_payload)
                _logger.info("auth_response.status_code: %d", auth_response.status_code)
                if auth_response.status_code == 200:
                    token = auth_response.json().get("token")
                    _logger.info("Authentication successful. Token received: %s", token)

                    # Prepare SMS headers and payload
                    sms_headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json",
                    }

                    _logger.info("Phone Number: %s", order.partner_id.phone)
                    _logger.info("Partner Name: %s", order.partner_id.name)
                    _logger.info("Order ID: %s", order.id)


                    sms_payload = {
                        "pingBackType": "0",
                        "pingBackId": "0",
                        "jsonData": {
                            "senderId": "CARLIA",
                            "templateId": "1107173563526518515",
                            "templateName": "carollia order placed message (www.carollia.com)",
                            "unicodeStatus": 0,
                            "messages": [
                                {
                                    "msisdn": order.partner_id.phone,  # Fetch the customer's phone number
                                    "message": f" Hi {order.partner_id.name}, your order {order.id} on Carollia has been successfully placed. We will notify you once it is shipped.",
                                    "customerReferenceId": str(order.id)  # Sales order ID
                                }
                            ]
                        },
                        "validationFlag": "1",
                        "validatyPeriod": "",
                        "data": ""
                    }

                    _logger.info("SMS Payload: %s", sms_payload)
                    _logger.info("SMS Headers: %s", sms_headers)
                    _logger.info("SMS URL: %s", sms_url)

                    # Send SMS
                    sms_response = requests.post(sms_url, json=sms_payload, headers=sms_headers)
                    _logger.info("sms_response.status_code: %d", sms_response.status_code)
                    if sms_response.status_code == 200:
                        sms_result = sms_response.json()
                        _logger.info("SMS sent successfully for Sale Order %s: %s", order.name, sms_result)
                    else:
                        _logger.error("Failed to send SMS for Sale Order %s. Status: %d, Response: %s",
                                      order.name, sms_response.status_code, sms_response.text)
                else:
                    _logger.error("Authentication failed for SMS service. Status: %d, Response: %s",
                                  auth_response.status_code, auth_response.text)
            except Exception as e:
                _logger.error("An error occurred while sending SMS for Sale Order %s: %s", order.name, str(e))

        return result

