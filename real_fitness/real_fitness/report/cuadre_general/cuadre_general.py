# Copyright (c) 2024, Rainier Polanco and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []
    return  get_columns(), get_data(filters),

def get_columns():
        return [
            {
                "label": _("Docto"),
                "fieldname": "name",
                "fieldtype": "Link",
                "options": "Sales Invoice",
                "width": 180
            },
            {
                "label": _("Facturado"),
                "fieldname": "grand_total",
                "fieldtype": "Currency",
                "width": 100
            },
            {
                "label": _("Total Efectivo"),
                "fieldname": "total_efectivo",
                "fieldtype": "Currency",
                "width": 100
            },
            {
                "label": _("Cheque"),
                "fieldname": "cheque",
                "fieldtype": "Currency",
                "width": 100
            },
            {
                "label": _("Transferencia"),
                "fieldname": "transferencia",
                "fieldtype": "Currency",
                "width": 100
            },
            {
                "label": _("Tarjetas"),
                "fieldname": "tarjetas",
                "fieldtype": "Currency",
                "width": 160
            },
            {
                "label": _("Nota Cred"),
                "fieldname": "credit_note",
                "fieldtype": "Currency",
                "width": 160                
            },
            {
                "label": _("CxC"),
                "fieldname": "cxc",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "label": _("Cambio"),
                "fieldname": "cambio",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "label": _("Efectivo"),
                "fieldname": "efectivo",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "label": _("Total Cobrado"),
                "fieldname": "total_cobrado",
                "fieldtype": "Currency",
                "width": 120
            }
        ]


def get_data(filters):
    result = []
    from_date = filters.get("from_date")
    to_date = filters.get("to_date")

    data = frappe.db.sql(f"""
        Select
            si.name,            
            si.grand_total,
            si.paid_amount,                       
            si.paid_amount - si.grand_total As cambio,
            si.paid_amount  As efectivo,
            si.paid_amount  As total_cobrado,
            sip.mode_of_payment
        From
            `tabSales Invoice` As si
        Inner Join 
            `tabSales Invoice Payment` sip 
        On 
            si.name = sip.parent
        Where   
            si.posting_date Between '{from_date}' And '{to_date}'
    """, as_dict=True)

    efectivo = 0
    cheque = 0
    transferencia = 0
    tarjetas = 0
    cxc = 0
    cambio = 0
    total_cobrado = 0
    giro_bancario = 0
    credit_note = 0

    for row in data:
        si = frappe.get_doc("Sales Invoice", row.name)

        if si.is_return:
            credit_note = si.grand_total
        for item in si.payments:
            if item.mode_of_payment == 'Efectivo':
                efectivo =+ item.amount
            if item.mode_of_payment == 'Cheque':
                cheque =+ item.amount
            elif item.mode_of_payment == 'Transferencia bancaria':
                transferencia =+ item.amount
            elif item.mode_of_payment == 'Tarjetas de credito':
                tarjetas =+ item.amount
            elif item.mode_of_payment == 'CxP':
                cxc = item.amount
            elif item.mode_of_payment == 'Giro bancario':
                giro_bancario = item.amount
            
        
        cambio = row.cambio
        total_cobrado = cheque + transferencia + tarjetas + cxc + efectivo + giro_bancario


        result.append([
            row.name,
            row.grand_total,
            row.paid_amount,
            cheque,
            transferencia,
            tarjetas,
            credit_note,
            cxc,
            cambio,
            efectivo,
            total_cobrado
        ])

    return result
