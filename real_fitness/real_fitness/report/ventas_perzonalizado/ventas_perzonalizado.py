# Copyright (c) 2024, Lewin Villar and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	return get_columns(), get_data(filters)



def get_columns():
	return [
			{
				"label": _("No. Factura"),
				"fieldname": "no_factura",
				"fieldtype": "Link",
				"options": "Sales Invoice",
				"width": 200
			},
			{
				"label": _("Fecha"),
				"fieldname": "fecha",
				"fieldtype": "Date",
				"width": 180
			},
			{
				"label": _("Cliente"),
				"fieldname": "cliente",
				"fieldtype": "Link",
				"options": "Customer",
				"width": 140
			},
			{
				"label": _("Producto"),
				"fieldname": "item",
				"fieldtype": "Link",
				"options": "Item",
				"width": 140
			},
			{
				"label": _("Cantidad"),
				"fieldname": "qty",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Precio UND"),
				"fieldname": "precio",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Monto Total"),
				"fieldname": "paid_amount",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Monto Pendiente"),
				"fieldname": "paid_pendiente",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Estado"),
				"fieldname": "estado",
				"fieldtype": "Data",
				"width": 140
			}
		]

def get_data(filters):
	query = f"""
		SELECT
			SI.name,
			SI.posting_date,
			SI.customer,
			SII.item_code,
			SII.qty,
			SII.rate,
			SII.amount,
			SI.outstanding_amount,
			SI.status
		
		FROM
			`tabSales Invoice` SI
		JOIN 
			`tabSales Invoice Item` SII
		ON
			SII.parent = SI.name
		WHERE
			SI.docstatus = 1 AND
			SI.posting_date BETWEEN '{filters.get("from_date")}' AND '{filters.get("to_date")}' 
	"""
	return frappe.db.sql(query)
