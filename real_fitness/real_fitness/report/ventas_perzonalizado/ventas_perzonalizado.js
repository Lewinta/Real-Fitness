// Copyright (c) 2024, Lewin Villar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Ventas Perzonalizado"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("Desde"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "to_date",
			"label": __("Hasta"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
	]
};
