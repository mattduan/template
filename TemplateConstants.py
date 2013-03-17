
TMPL = 'tmpl'
ZPT  = 'zpt'

TEMPLATE_LIST = [TMPL, ZPT]
TEMPLATE_DICT = {
	TMPL : {
		'manager'   : 'TMPLTemplateManager',
		'processor' : 'TMPLTemplateProcessor',
		},
	ZPT  : {
		'manager'   : 'ZPTTemplateManager',
		'processor' : 'ZPTTemplateProcessor',
		},
	}

