{
    'name':'Manpower_Request_Form',
    'version':'1.0',
    'summary':'module to create form to request manpower',
    'sequence':5,
    'author':'catalist',
    'license':'LGPL-3',
    'depends':['base','hr','mail','hr_recruitment'],
    'data':[
        'security/ir.model.access.csv',
        'security/manpower_request.xml',

        'views/menu.xml',
        # 'views/manpower.xml',
        'data/sequence_data.xml',

    ],
    'installable':True,
    'application':True,
    'auto_install':False


}