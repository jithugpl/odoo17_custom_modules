import base64

from odoo import http
from odoo.http import request


class CustomerRegistrationController(http.Controller):

    @http.route('/customer/register', type='http', auth="public", website=True, csrf=True)
    def customer_register(self, **post):
        print("/customer/register' %s" % post)

        # # Create a new customer registration record
        # request.env['customer.registration'].sudo().create({
        #     'name': post.get('name'),
        #     'email': post.get('email'),
        #     'phone': post.get('phone'),
        #     'address': post.get('address'),
        # })
        # Redirect to a confirmation page
        return request.render("website_customer_registration.customer_registration_page")

        # Route to handle form submission

    @http.route('/customer/register/submit', type='http', auth="public", website=True, methods=['POST'], csrf=True)
    def customer_register_submit(self, **post):
        print("Received registration data: %s" % post)

        # Create a new customer registration record only on form submission
        # request.env['customer.registration'].sudo().create({
        #     'name': post.get('name'),
        #     'email': post.get('email'),
        #     'phone': post.get('phone'),
        #     'address': post.get('address'),
        # })
        partner=request.env['res.partner'].sudo().create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
            'street': post.get('address'),
            'customer_rank': 1,  # Set customer rank to 1 to identify it as a customer
        })
        print("Created partner ID: %s" %  partner.id)
        # Redirect to a confirmation page after successful submission
        return request.render("website_customer_registration.customer_registration_confirmation_page", {
            'partner_id': partner.id
        })
    #
    @http.route('/customer/files', type='http', auth="public", website=True, csrf=True)
    def customer_files(self, **post):
    #
    #     email = post.get('mail_id')
    #     file_name = post.get('file_name')
    #     uploaded_file = post.get('file')
    #
    #     # Convert the uploaded file into base64 to store it in Odoo's binary field
    #     if uploaded_file and file_name:
    #         file_content = uploaded_file.read()
    #         file_base64 = base64.b64encode(file_content)
    #
    #         # Find the corresponding registration by email
    #         registration = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
    #         if registration:
    #             # Create a new order line with the uploaded file
    #             request.env['res.partner'].sudo().create({
    #                 'name': 'Customer Name',
    #                 'registration_id': registration.id,
    #                 'file_name': file_name,
    #                 'file': file_base64,
    #             })
    #
    #             # Redirect to a confirmation page after successful upload
    #             return request.render("website_customer_registration.file_upload_confirmation", {
    #                 'file_name': file_name,
    #                 'registration_id': registration.id,
    #             })
        return request.render("website_customer_registration.file_upload_form")

    @http.route('/customer/upload/file/<int:partner_id>', type='http', auth="public", website=True,  methods=['POST','GET'], csrf=True)
    def customer_file_upload(self,partner_id, **post):
            print(post)
            # Retrieve the partner ID passed from the previous page (after registration)
            # partner_id = post.get('partner_id')
            print("Retrieved partner_id:", partner_id)
            file_name = post.get('file_name')  # Get the file name from the form
            uploaded_file = post.get('file')  # Get the uploaded file from the form
            print("uploaded_file",uploaded_file)
            print("file_name",file_name)

            # Ensure that the uploaded file exists
            if uploaded_file and file_name:
                file_content = uploaded_file.read()  # Read the file content
                file_base64 = base64.b64encode(file_content)  # Encode the file content to base64
                print(file_base64)

                # Locate the partner using the provided partner ID
                partner = request.env['res.partner'].sudo().browse(partner_id)
                print("partner", partner)
                print("partner_id", partner_id)
                print("partner.id", partner.id)
                print("file_name", file_name)
                print(file_base64)
                if partner.exists():
                    # Update the existing partner record with the uploaded file's name and content
                    partner.sudo().write({
                        'file_name': file_name,  # Set the file name
                        'file_data': file_base64,  # Set the file content (base64 encoded)
                    })
                    updated_partner = request.env['res.partner'].sudo().browse(partner_id)
                    print("Updated file_name:", updated_partner.file_name)
                    print("Updated file_data (base64):", updated_partner.file_data)

                return request.render("website_customer_registration.file_upload_confirmation", {
                    'file_name': file_name,
                    'partner_id': partner_id,
                })
            else:
                # This block executes if uploaded_file or file_name is missing/invalid
                print("File upload failed or missing data")
                print("Uploaded file:", uploaded_file)
                print("File name:", file_name)

                # Optionally, return an error message or re-render the form with an error context
                return request.render("website_customer_registration.file_upload_form", {
                    'partner_id': partner_id,
                    'error_message': "File upload failed. Please ensure a file and file name are provided."
                })

    # csrf_token = post.get('csrf_token')
        # if csrf_token != request.csrf_token():
        #     return request.render("website.403")
        # Retrieve registration by email (mail_id) from the form
        # global file_base64
        # email = post.get('mail_id')
        # file_name = post.get('file_name')
        # uploaded_file = post.get('file')
        # # if not file_name:
        # #     print("file_name is empty",uploaded_file)
        #
        # # Convert the uploaded file into base64 to store it in Odoo's binary field
        # if uploaded_file and file_name:
        #     file_content = uploaded_file.read()
        #     file_base64 = base64.b64encode(file_content)
        #
        #     # Find the corresponding registration by email
        # registration = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        # if registration:
        #     # Create a new order line with the uploaded file
        #     # request.env['res.partner'].sudo().create({
        #     #     # 'registration_id': registration.id,
        #     #     'file_name': file_name,
        #     #     'file':file_base64,
        #     # })
        #
        #     request.env['ir.attachment'].sudo().create({
        #         'name': file_name,
        #         'datas': file_base64,
        #         'res_model': 'res.partner',
        #         'res_id': registration.id,
        #         'type': 'binary',  # Binary type is required for file attachments
        #     })
        # registration = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        # if registration:
        #         # Save the file directly to the res.partner record
        #     registration.sudo().write({
        #             'file_data': file_base64,
        #             'file_name': file_name,
        #         })
        #
        #     # Redirect to a confirmation page after successful upload
        #     return request.render("website_customer_registration.file_upload_confirmation", {
        #         'file_name': file_name,
        #         'registration_id': registration.id,
        #     })
        # return request.render("website_customer_registration.file_upload_form")

    @http.route('/chatter/send_message', type='http', auth="public", methods=['POST'], csrf=True)
    def send_message(self, registration_id, **post):
        message_body = post.get('message_body')

        if message_body and registration_id:
            # Locate the specific record in customer.registration model
            registration = request.env['res.partner'].sudo().browse(int(registration_id))
            if registration.exists():
                # Post a message to the chatter of the customer.registration record
                registration.message_post(
                    body=message_body,
                    subtype_xmlid="mail.mt_comment"  # Post as a comment in chatter
                )

        # Redirect back to the same page, dynamically adding registration_id
        return request.redirect(f'/customer/registration/{registration_id}')

    @http.route('/customer/registration/<int:registration_id>', type='http', auth='public', website=True)
    def view_registration_files(self, registration_id):
        # Fetch the customer registration record
        registration = request.env['res.partner'].browse(registration_id)

        # Prepare the list of files to display
        files = []
        if registration.file_data:  # Check if the file_data field contains data
            # Add the file record itself to the list (not just a dict)
            files.append(registration)

                # Fetch the chatter messages for the registration
        messages = request.env['mail.message'].sudo().search([
            ('res_id', '=', registration_id),
            ('model', '=', 'res.partner')
        ])

        # Fetch the activities for the registration
        activities = request.env['mail.activity'].sudo().search([
            ('res_id', '=', registration_id),
            ('res_model', '=', 'res.partner')
        ])

        # Render the template and pass the file data along with chatter data
        return request.render('website_customer_registration.registration_files', {
            'registration': registration,
            'files': files,  # Pass the file data to the template
            'messages': messages,
            'activities': activities,
        })

    @http.route('/my/documents', type='http', auth='public', website=True)
    def documents(self):
        # Fetch all customer registrations and their associated order lines
        registrations = request.env['res.partner'].search([])
        return request.render('website_customer_registration.template_documents', {
            'registrations': registrations,
        })

    @http.route(['/form/submit'], type='http', auth='public', website=True)
    def file_upload(self, redirect=None, **kw):
        current_partner_id = request.env.user.partner_id
        file = kw.get('att')
        if file:
            file_name = file.filename
            attachment_id = request.env['ir.attachment'].create({
                'name': file_name,
                'type': 'binary',
                'datas': base64.b64encode(file.read()),
                'res_model': current_partner_id._name,
                'res_id': current_partner_id.id
            })
            # Link attachment to the partner
            current_partner_id.write({
                'file_attachment_ids': [(4, attachment_id.id)],
            })
    # def file_upload(self, redirect=None, **kw):
    #     current_partner_id = request.env.user.partner_id
    #     file_name = kw.get('att').filename
    #     file = kw.get('att')
    #     attachment_id = request.env['ir.attachment'].create({
    #         'name': file_name,
    #         'type': 'binary',
    #         'datas': base64.b64encode(file.read()),
    #         'res_model': current_partner_id._name,
    #         'res_id': current_partner_id.id
    #     })
    #     current_partner_id.update({
    #         file_attachment_ids: [(4, attachment_id.id)],
    #     })
