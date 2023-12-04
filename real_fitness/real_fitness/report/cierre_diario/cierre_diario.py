# Copyright (c) 2023, Rey ferreras and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import Query, Criterion, Field, functions as fn
from frappe.query_builder.custom import ConstantColumn


def execute(filters=None):
	return get_columns(filters), get_data(filters)

def get_columns(filters):
	if filters.summary:
		return [
			{
				"label": _("User"),
				"fieldname": "user",
				"fieldtype": "Data",
				"width": 200
			},
			{
				"label": _("Mode of Payment"),
				"fieldname": "mode_of_payment",
				"fieldtype": "Data",
				"width": 180
			},
			{
				"label": _("Opening"),
				"fieldname": "opening",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Income"),
				"fieldname": "income",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Expenses"),
				"fieldname": "expenses",
				"fieldtype": "Currency",
				"width": 140
			},
			{
				"label": _("Balance"),
				"fieldname": "balance",
				"fieldtype": "Currency",
				"width": 140
			},
		]
	else:
		return [
			{
				"label": _("Document"),
				"fieldname": "document",
				"fieldtype": "Link",
				"options": "Payment Entry",
				"width": 190
			},
			{
				"label": _("Document Type"),
				"fieldname": "document_type",
				"fieldtype": "Data",
				"width": 180
			},
			{
				"label": _("User"),
				"fieldname": "user",
				"fieldtype": "Data",
				"width": 200
			},
			{
				"label": _("Mode of Payment"),
				"fieldname": "mode_of_payment",
				"fieldtype": "Data",
				"width": 180
			},
			{
				"label": _("Date"),
				"fieldname": "date",
				"fieldtype": "Date",
				"width": 100
			},
			{
				"label": _("Party"),
				"fieldname": "party",
				"fieldtype": "Data",
				"width": 300
			},
			{
				"label": _("Income"),
				"fieldname": "income",
				"fieldtype": "Currency",
				"width": 140,
				"precision": 2
			},
			{
				"label": _("Expenses"),
				"fieldname": "expenses",
				"fieldtype": "Currency",
				"width": 140,
				"precision": 2
			},
			{
				"label": _("Balance"),
				"fieldname": "balance",
				"fieldtype": "Currency",
				"width": 140,
				"precision": 2
			},

	]

def get_data(filters):
	data = []
	if filters.summary:
		query = get_opening_entry(filters) + get_sales_payments(filters) + get_purchase_payments(filters) + get_in_payment_entries(filters) + get_out_payment_entries(filters)
		return frappe.qb.from_(query).select(
			query.user,
			query.mode_of_payment,
			fn.Sum(query.opening).as_("opening"),
			fn.Sum(query.income).as_("income"),
			fn.Sum(query.expenses).as_("expenses"),
			fn.Sum(query.balance).as_("balance")
		).groupby(query.user, query.mode_of_payment).run(as_dict=True)
	else:
		query = get_opening_entry(filters) + get_sales_payments(filters) + get_purchase_payments(filters) + get_in_payment_entries(filters) + get_out_payment_entries(filters)
		
		# data = sorted(data, key=lambda x: x["date"])
		return frappe.qb.from_(query).select('*').run(as_dict=True)
		
		return data

def get_opening_entry(filters):
	POE = frappe.qb.DocType("POS Opening Shift")
	POED = frappe.qb.DocType("POS Opening Shift Detail")
	USR = frappe.qb.DocType("User")

	conditions = [ 
		POED.amount > 0,
		POE.docstatus == 1 
	]
	
	if filters.get("user"):
		conditions.append(POE.user == filters.get("user"))
	
	if filters.get("date"):
		conditions.append(POE.posting_date == filters.get("date"))

	return Query.from_(POE).select(
		POE.name.as_("document"),
		ConstantColumn(_("POS Opening Shift")).as_("document_type"),
		USR.full_name.as_("user"),
		POED.mode_of_payment,
		POE.posting_date.as_("date"),
		USR.full_name.as_("party"),
		POED.amount.as_("opening"),
		(POED.amount * 0.0).as_("income"),
		(POED.amount * 0.0).as_("expenses"),
		(POED.amount * 0.00).as_("balance")
	).join(POED).on(
		POE.name == POED.parent
	).join(USR).on(
		POE.user == USR.name
	).where( Criterion.all(conditions) )

def get_sales_payments(filters):
	SINV = frappe.qb.DocType("Sales Invoice")
	POI = frappe.qb.DocType("POS Invoice")
	SIP = frappe.qb.DocType("Sales Invoice Payment")
	USR = frappe.qb.DocType("User")
	
	conditions = [ SINV.docstatus == 1 ]
	
	if filters.get("date"):
		conditions.append(SINV.posting_date >= filters.get("date"))
		conditions.append(SINV.posting_date <= filters.get("date"))
	
	if filters.get("user"):
		conditions.append(SINV.owner == filters.get("user"))
	
	invoice_no = Query.from_(POI).select(  fn.Max(POI.name) ).where(
		POI.consolidated_invoice == SINV.name
	)

	return Query.from_(SINV).select(
		fn.Coalesce(invoice_no, SINV.name).as_("document"),
		ConstantColumn(_("Sales Invoice")).as_("document_type"),
		USR.full_name.as_("user"),
		SIP.mode_of_payment,
		SINV.posting_date.as_("date"),
		SINV.customer_name.as_("party"),
		(SIP.amount * 0.00).as_("opening"),
		SIP.amount.as_("income"),
		(SIP.amount * 0.00).as_("expenses"),
		SIP.amount.as_("balance")
	).join(SIP).on(
		SINV.name == SIP.parent
	).join(USR).on(
		SINV.owner == USR.name
	).where( Criterion.all(conditions) )

def get_purchase_payments(filters):
	PINV = frappe.qb.DocType("Purchase Invoice")
	USR = frappe.qb.DocType("User")
	
	conditions = [ PINV.docstatus == 1, PINV.paid_amount > 0 ]
	
	if filters.get("date"):
		conditions.append(PINV.posting_date >= filters.get("date"))
		conditions.append(PINV.posting_date <= filters.get("date"))
	
	if filters.get("user"):
		conditions.append(PINV.owner == filters.get("user"))
	
	return Query.from_(PINV).select(
		PINV.name.as_("document"),
		ConstantColumn(_("Purchase Invoice")).as_("document_type"),
		USR.full_name.as_("user"),
		PINV.mode_of_payment.as_("mode_of_payment"),
		PINV.posting_date.as_("date"),
		PINV.supplier_name.as_("party"),
		(PINV.paid_amount * 0.0).as_("opening"),
		(PINV.grand_total * 0.00).as_("income"),
		(PINV.paid_amount * 1.0).as_("expenses"),
		-PINV.grand_total.as_("balance")
	).join(USR).on(
		PINV.owner == USR.name
	).where(
		Criterion.all(conditions)
	)

def get_in_payment_entries(filters):
	PE = frappe.qb.DocType("Payment Entry")
	USR = frappe.qb.DocType("User")

	conditions = [ PE.docstatus == 1 ]
	if filters.get("date"):
		conditions.append(PE.posting_date >= filters.get("date"))
		conditions.append(PE.posting_date <= filters.get("date"))
	
	if filters.get("user"):
		conditions.append(PE.owner == filters.get("user"))	

	return  Query.from_(PE).select(
		PE.name.as_("document"),
		ConstantColumn(_("Payment Entry")).as_("document_type"),
		USR.full_name.as_("user"),
		PE.mode_of_payment,
		PE.posting_date.as_("date"),
		PE.party_name.as_("party"),
		(PE.paid_amount * 0.0).as_("opening"),
		PE.paid_amount.as_("income"),
		(PE.paid_amount * 0.0).as_("expenses"),
		(PE.paid_amount).as_("balance")
	).join(USR).on(
		PE.owner == USR.name
	).where(
		Criterion.all(conditions + [PE.payment_type == "Receive"])
	)

def get_out_payment_entries(filters):
	PE = frappe.qb.DocType("Payment Entry")
	USR = frappe.qb.DocType("User")

	conditions = [ PE.docstatus == 1 ]
	if filters.get("date"):
		conditions.append(PE.posting_date >= filters.get("date"))
		conditions.append(PE.posting_date <= filters.get("date"))
	
	if filters.get("user"):
		conditions.append(PE.owner == filters.get("user"))
	
	return Query.from_(PE).select(
		PE.name.as_("document"),
		ConstantColumn(_("Payment Entry")).as_("document_type"),
		USR.full_name.as_("user"),
		PE.mode_of_payment,
		PE.posting_date.as_("date"),
		PE.party_name.as_("party"),
		(PE.paid_amount * 0).as_("opening"),
		(PE.paid_amount * 0).as_("income"),
		(PE.paid_amount * 1.0).as_("expenses"),
		(PE.paid_amount * -1).as_("balance")
	).join(USR).on(
		PE.owner == USR.name
	).where(
		Criterion.all(conditions + [PE.payment_type == "Pay"])
	)