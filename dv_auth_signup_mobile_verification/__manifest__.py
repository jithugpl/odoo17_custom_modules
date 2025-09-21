{
    "name": "DV auth signup mobile verification",
    "summary": "Force uninvited users to use a good mobile for signup",
    "version": "17.0.1.0.0",
    "category": "Datavalley",
    "author": "Datavalley Web Service ",
    "license": "AGPL-3",
    "depends": ["auth_signup","auth_signup_verify_email"],
    "external_dependencies": {"python": ["lxml", "email_validator"]},
    "data": ["views/mobile_view.xml",

             ],
    "installable": True,
}
