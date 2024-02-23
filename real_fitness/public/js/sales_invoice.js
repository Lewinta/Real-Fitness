{
    function refresh(frm) {
        frappe.run_serially([
            () => hide_custom_buttons(frm),
            () => add_custom_buttons(frm),
        ]);
    }

    function hide_custom_buttons(frm) {
        hide_healthcare_services_button(frm);
    }

    function add_custom_buttons(frm) {
        add_healthcare_services_button(frm);
    }

    function hide_healthcare_services_button(frm) {
        setTimeout(() => {
            frm.remove_custom_button("Healthcare Services", "Get Items From");
        }, 1000);
    }

    function add_healthcare_services_button(frm) {
        const label = "Patient Encounter";
        const action = () => {
            multiselect_dialog_for_patient_encounter(frm);
        };
        const group = "Get Items From";

        frm.add_custom_button(label, action, group);
    }

    function multiselect_dialog_for_patient_encounter(frm) {
        const doctype = "Patient Encounter";
        const target = frm.doc;
        const setters = {
            patient: target.patient,
        };
        const get_query = () => {
            return {
                filters: {
                    docstatus: 1,
                    patient: setters.patient,
                },
            }
        };
        const action = (selections) => {
            const method = [
                "real_fitness",
                "controllers",
                "sales_invoice",
                "sales_invoice",
                "get_items_from_patient_encounter_in_clinical_procedure",
            ].join(".");

            const args = {
                selections,
            };

            frappe.call({ method, args }).then((response) => {
                const { message: items } = response;

                frm.clear_table("items");

                const add_item_row = (item, rate) => {
                    const row = frm.add_child("items");
                    frappe.model.set_value(row.doctype, row.name, "item_code", item).then(() => {
                        row.rate = rate;
                        frm.trigger("calculate_taxes_and_totals");
                    });
                }


                if (items) {
                    items.forEach((item) => {
                        add_item_row(item.item_code, item.rate);
                    });

                }
                d.dialog.hide();
            });

        };

        let d = new frappe.ui.form.MultiSelectDialog({
            doctype,
            target,
            setters,
            get_query,
            action,
        });

    }


    frappe.ui.form.on("Sales Invoice", {
        refresh,
    });
}
