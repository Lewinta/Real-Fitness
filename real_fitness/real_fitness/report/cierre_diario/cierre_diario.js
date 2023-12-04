// Copyright (c) 2023, Rey Ferreras and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cierre Diario"] = {
	"filters": [
		{
			"fieldname": "date",
			"label": __("Date"),
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "user",
			"label": __("User"),
			"fieldtype": "Link",
			"options": "User",
			"default": frappe.session.user,
			"read_only": !frappe.user.has_role(["Manager", "System Manager"])
			// "reqd": 1,
		},
		{
			"fieldname": "summary",
			"label": __("Summary"),
			"fieldtype": "Check",
			"default": 1
		}
	],
	"formatter": function (value, row, column, data, default_formatter) {
		const raw_value = value;
		value = default_formatter(value, row, column, data);

		if (column.id == "income")
			value = `<span style='color: ${raw_value > 0 ? 'green' : 'black'}'>` + value + "</span>";
		
		if (column.id == "expenses")
			value = `<span style='color: ${raw_value > 0 ? 'red' : 'black'}'>` + value + "</span>";
		
		if (column.id == "balance") 
			value = `<span style='color: ${get_color(column.id, raw_value)}'>` + value + "</span>";
		

		return value;
	}
	
};

function get_color(column, value){
	if (value > 0.0) {
		return "green";
	} else if (value < 0.0) {
		return "red";
	} else {
		return "black";
	}
}
