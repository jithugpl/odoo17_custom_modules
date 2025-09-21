{
    "name": "Razorpay Payment Gateway Integration",
    "version": "1.0",
    "category": "Website/Payment",
    "summary": "Integrate Razorpay via Axis Bank for Website Sales",
    "depends": ["website_sale", "payment"],
    "data": [
        "views/payment_razorpay_templates.xml",
        "views/payment_acquirer_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "/razorpay_payment_gateway/static/js/razorpay_checkout.js",
        ],
    },
    "installable": True,
    "application": False,
}