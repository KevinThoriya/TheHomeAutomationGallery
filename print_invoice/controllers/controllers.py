# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request
from odoo.addons.web.controllers.main import ReportController
from odoo.addons.print_invoice.invoice_print.report_invoice import generate_pdf_content
import json
class ReportPrintController(ReportController):

    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, context=None):
        print(data, context)
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        
        if 'print_invoice.invoice_report_template' in url or 'report_invoice_with_payments' in url:    
            reportname = url.split('/report/pdf/')[1].split('?')[0]
            reportname, docids = reportname.split('/')
            ids = [int(x) for x in docids.split(",")]
            invoice = request.env['account.move'].browse(ids)
            print(json.loads(invoice.tax_totals_json))
            invoiceD = json.loads(invoice.tax_totals_json)
            pdf = generate_pdf_content({
                'companyDetail': [
                    ('The Home Automation Gallery', 12), 
                    ('', 1), 
                    ('f-6/7, Sky Mall', 8),
                    ('Morbi - 363641', 8),
                    ('Gujarat, India', 8),
                    ('', 1),
                    ( 'www.thehomeautomationgallery.com', 8),
                    ( 'thehomeautomationgallery@gmail.com', 8)],
                'invoice': {
                    'title': f"Customer Invoices {invoice.name} ",
                    'date': invoice.invoice_date.strftime('%m/%d/%Y'),
                    'due_date': invoice.invoice_date.strftime('%m/%d/%Y'),
                    'items': 
                    [['DESCRIPTION','QUANTITY','UNIT PRICE','TAXES','AMOUNT']] + [
                        [
                        line.product_id.name,
                        line.price_unit,
                        line.quantity,
                        ', '.join(line.tax_ids.mapped('name')),
                        line.price_subtotal
                        ]
                        for line in invoice.invoice_line_ids
                     ],
                    'payment_communication': {
                        'title': "Payment Communication",
                        'value': invoice.name
                    },
                    'amounts': [['Untaxed Amount', invoiceD.get('formatted_amount_untaxed')]] + [
                        [tax.get('tax_group_name'), tax.get('formatted_tax_group_amount')] for tax in invoiceD.get('groups_by_subtotal').get('Untaxed Amount') 
                    ] + [['Total',invoiceD.get('formatted_amount_total')]],
                    'total': f'{invoiceD.get("amount_total")}',
                }
            })
            pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
            return request.make_response(pdf, headers=pdfhttpheaders)
        else: 
            return super(ReportPrintController, self).report_download(data, context)

