#-*- coding: utf-8 -*-

{
	"name": "Vit_stock_opname",
	"version": "1.0", 
	"depends": [
		'base','mrp','product','barcodes'
	],
	'author': 'firmanrizaldiyusup@gmail.com',
	'website': 'http://www.vitraining.com',
	"summary": "membuat addon vit_stock_opname",
	"description": """
-membuat menu SON WIP
-export ke excel
""",
	"data": [
		"security/ir.model.access.csv",
		"view/menu.xml",
		"view/stock_opname.xml",
		"view/workcenter.xml",
		"sequence/squence.xml",
		# "data/workorder.xml",
  
		# "report/stock_opname.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}