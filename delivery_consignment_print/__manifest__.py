{
    'name':'delivery_consignment_print',
    'version':'1.0',
    'summary':'module to print delivery conignment',
    'sequence':5,
    'author':'catalist',
    'license':'LGPL-3',
    'depends':['stock'],
    'data':[
        'views/view.xml',
        'views/consignment_print.xml',
        # 'views/delivery.xml',

    ],
    'installable':True,
    'application':True,
    'auto_install':False


}