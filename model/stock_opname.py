
from odoo import api, fields, models
import time
import datetime
from io import BytesIO
import xlsxwriter
import base64
import logging
from odoo.exceptions import Warning 
_logger = logging.getLogger(__name__)



class stock_opname(models.Model):

    _name = "vit.stock_opname"
    _inherit = ["barcodes.barcode_events_mixin"]
    
    
    name = fields.Char( readonly=True, string="No Kartu SON",  help="")
    tanggal = fields.Date( string="Tanggal",  required=False, 
                        default=lambda self: time.strftime("%Y-%m-%d"))
    
    
    storage_id = fields.Many2one(
        string='Storage',
        comodel_name='storage.proses'
    )

    data_entry = fields.Many2one('res.users', 'Data Entry', default=lambda self: self.env.user, track_visibility='onchange')
    
    No_po = fields.Many2one("mrp.production", string="No P/O",  help="")
    
  
    No_kartu = fields.Selection([('1/1', '1/1'), 
                                 ('1/3', '1/3'), 
                                 ('1/9', '1/9')], "No Kartu" , default='1/1' )
    
    
    
    item_id = fields.Char( string="Item ID", related='No_po.product_id.default_code' ,
                            readonly=True )
    
    item_name = fields.Char(related='No_po.product_id.name', string="Item Name",)
    
    # Customer = fields.Char(related='No_po.customer_id.name', string="Customer",)
    Customer = fields.Char(related='No_po.name', string="Customer",)
  
    Qty = fields.Float(string="Qty [kg]",) 
    
    Proses = fields.Many2one(
        string='Proses',
        comodel_name='mrp.workcenter',
    )
    
    No_kartu_son = fields.Char( string="nokartu",  help="")
    keterangan = fields.Char( string="Keterangan",  help="")
    data = fields.Binary('File')
    
    
    export_excels = fields.Boolean(
        string='Expert Excel', dafault=False
    )
    
    
    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vit.stock_opname') or 'Error Number!!!'
        return super(stock_opname, self).create(vals)
    



    @api.onchange('No_po')
    def onchange_doc_template_id(self):
        
        if self.No_po:
            iniqtynya = self.No_po.product_qty
            self.Qty = iniqtynya

            return {'domain': {'Qty': [('product_qty', '=', iniqtynya)]}}
        
        else:
            self.Qty = False
            return {'domain': {'Qty': [('product_qty', '!=', False)]}}
        
        
# //////////////////////////////////////////////////open barcode/////////////////////////////////////////
        
    def _add_mo_barcode(self, barcode):
        
        mo = self.env["mrp.production"].search([('name','=', barcode)])
        
        if mo :
            self.No_po = mo.id
        
    def on_barcode_scanned(self, barcode):
        self._add_mo_barcode(barcode)
        
# //////////////////////////////////////////////////close barcode/////////////////////////////////////////

# //////////////////////////////////////////////////open excel/////////////////////////////////////////
        
    def cell_format(self, workbook):
        cell_format = {}
        cell_format['title'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,
            'font_name': 'Arial',
        })
        cell_format['header'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'border': True,
            'font_name': 'Arial',
        })
        cell_format['content'] = workbook.add_format({
            'font_size': 11,
            'border': False,
            'font_name': 'Arial',
        })
        cell_format['content_float'] = workbook.add_format({
            'font_size': 11,
            'border': True,
            'num_format': '#,##0.00',
            'font_name': 'Arial',
        })
        cell_format['total'] = workbook.add_format({
            'bold': True,
            'num_format': '#,##0.00',
            'border': True,
            'font_name': 'Arial',
        })
        return cell_format, workbook


    @api.multi
    def print_excel(self):
        obj_stock_opname = self.env["vit.stock_opname"].search([('export_excels','=',False)])
        
        headers = [
            "External ID",
            "Reference",
            "Work Orders/Display Name",
            "Work Orders/Work Order",
            "Work Orders/Status",
            "Work Orders/Current Qty",
            "Work Orders/Produced Qty",
        ]

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        cell_format, workbook = self.cell_format(workbook)

        if not obj_stock_opname :
            raise Warning("Data tidak ditemukan. Mohon Create SOP WIP dulu")

        worksheet = workbook.add_worksheet()
        worksheet.set_column('A:ZZ', 30)
        column_length = len(headers)

        column = 0
        row = 0
        for col in headers:
            worksheet.write(row, column, col, cell_format['header'])
            column += 1

        ########### contents
        row = 1
        final_data=[]
       
        for data in obj_stock_opname :
            final_data.append([
                "Son"+ str(data.id),
                data.No_po.name,
                data.storage_id.name,
                data.Proses.name,
                "Progress",
                data.Qty,
                data.Qty,
            ])
            
            data.export_excels=True
        

        for data in final_data:
            column = 0
            for col in data:
                worksheet.write(row, column, col, cell_format['content'] if column<0 else  cell_format['content_float'])
                column += 1
            row += 1

        workbook.close()
        result = base64.encodestring(fp.getvalue())
        filename = self.name + '-' + str(self.tanggal) + '%2Exlsx'
        self.write({'data':result})
        url = "web/content/?model="+self._name+"&id="+str(self.id)+"&field=data&download=true&filename="+filename
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }