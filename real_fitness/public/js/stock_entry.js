// Copyright (c) 2024, Yefri Tavarez and contributors
// For license information, please see license.txt
/* eslint-disable */

{
    function refresh(frm) {
        add_fetches(frm);
        set_queries(frm);
    }

    function set_queries(frm) {
        set_target_cabin_query(frm);
        // set_from_warehouse_query(frm);
        // set_to_warehouse_query(frm);
    }

    function add_fetches(frm) {
        add_to_warehouse_fetch(frm);
    }

    function set_target_cabin_query(frm) {
        const fieldname = "target_cabin";
        function get_query() {
            const filters = {
                warehouse_type: "Cabin",
            };

            return { filters };
        }

        frm.set_query(fieldname, get_query);
    }

    function set_from_warehouse_query(frm) {
        const { doc } = frm;

        const is_warehouse_staff = frappe.user.has_role([
            "Warehouse Staff", "Warehouse Staff Privileged"
        ]);

        if (!is_warehouse_staff) {
            return ; // skip for non-warehouse staff
        }

        const fieldname = "from_warehouse";
        function get_query() {
            const filters = {
                warehouse_type: ["!=", "Transit"],
                company: doc.company,
                is_group: 0,
            };

            return { filters };
        }
        
        frm.set_query(fieldname, get_query);
    }

    function set_to_warehouse_query(frm) {
        const is_warehouse_staff = frappe.user.has_role([
            "Warehouse Staff", "Warehouse Staff Privileged"
        ]);

        if (!is_warehouse_staff) {
            return ; // skip for non-warehouse staff
        }

        const fieldname = "to_warehouse";
        function get_query() {
            const filters = {
                warehouse_type: ["=", "Transit"],
            };

            return { filters };
        }
        
        frm.set_query(fieldname, get_query);
    }

    function add_to_warehouse_fetch(frm) {
        const link_name = "target_cabin";
        const source_name = "default_in_transit_warehouse";
        const target_name = "to_warehouse";

        frm.add_fetch(link_name, source_name, target_name);
    }

    frappe.ui.form.on("Stock Entry", {
        refresh,
    });
}