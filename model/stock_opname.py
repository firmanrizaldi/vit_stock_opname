
from odoo import api, fields, models
import time
import datetime
import logging
_logger = logging.getLogger(__name__)



class stock_opname(models.Model):

    _name = "vit.stock_opname"
    
    name = fields.Char( readonly=True, string="No Kartu SON",  help="")
    tanggal = fields.Date( string="Tanggal",  required=False, 
                        default=lambda self: time.strftime("%Y-%m-%d"))
    
    
    # Storage = fields.Selection([('heading', 'HEADING'), 
    #                              ('rolling', 'ROLLING'), 
    #                              ('furnace', 'FURNACE'), 
    #                              ('plating', 'PLATING'), 
    #                              ('fq', 'FQ')], "Storage" , default='heading' )
    
    
    Storage = fields.Char(
        string='storage', 
        compute='_compute_storage' )
            
    @api.depends('Storage','Proses')
    def _compute_storage(self):
        string = str(self.Proses.name)
        for record in self:
            if 'H' in string:
                record.Storage = "HEADING"
            elif 'R' in string:
                record.Storage = "ROLLING."
            elif 'PL' in string:
                record.Storage = "PLATING."
            elif 'FQ' in string:
                record.Storage = "FQ."
            elif 'F' == string:
                record.Storage = "FURNACE."

        
    @api.onchange('Proses')
    def onchange_storage(self):
        string = str(self.Proses.name)
        
        if 'H' in string:
            self.Storage = "HEADING"
        elif 'R' in string:
            self.Storage = "ROLLING."
        elif 'PL' in string:
            self.Storage = "PLATING."
        elif 'FQ' in string:
            self.Storage = "FQ."
        elif 'F' == string:
            self.Storage = "FURNACE."

            
        
    
    
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
    
    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vit.stock_opname') or 'Error Number!!!'
        return super(stock_opname, self).create(vals)
    
    keterangan = fields.Char( string="Keterangan",  help="")



    @api.onchange('No_po')
    def onchange_doc_template_id(self):
        
        if self.No_po:
            iniqtynya = self.No_po.product_qty
            self.Qty = iniqtynya

            return {'domain': {'Qty': [('product_qty', '=', iniqtynya)]}}
        
        else:
            self.Qty = False
            return {'domain': {'Qty': [('product_qty', '!=', False)]}}