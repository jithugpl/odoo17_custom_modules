{
    "name": "Owl Demo",
    "version": "1.0",
    "category": "Website",
    "depends": ["base", "web"],
    "assets": {
        "web.assets_backend": [
            # "owl_demo/static/src/js/components/CounterComponent.js",
            # "owl_demo/static/src/xml/CounterComponent.xml",
        ],
    },
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/owl_demo_templates.xml",
        "views/views.xml",
        "views/views_assests.xml"
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
