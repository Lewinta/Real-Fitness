// Copyright (c) 2023, Miguel Higuera and contributors
// For license information, please see license.txt
{

    function refresh(frm) {
        add_custom_buttons(frm);
    }

    function add_custom_buttons(frm) {
        add_send_nutritional_plan_button(frm);
    }

    function add_send_nutritional_plan_button(frm) {
        const label = __("Send Nutritional Plan");
        const action = () => {
            dialog_send_nutritional_plan(frm);
        }

        frm.add_custom_button(label, action);
    }

    function dialog_send_nutritional_plan(frm) {
        const title = __("Nutritional Plan Selection");
        const fields = [
            {
                "label": __("Filters"),
                "fieldtype": "Section Break",
            },
            {
                "label": __("Purpose"),
                "fieldtype": "Select",
                "fieldname": "purpose",
                "options": [
                    "Lose weight",
                    "Increase Muscle Mass"
                ],
                change() {
                    const { nutritional_plan } = dialog.fields_dict;
                    nutritional_plan.set_value("");
                }
            },
            {
                "fieldtype": "Column Break",
            },
            {
                "label": __("Calorie Count"),
                "fieldtype": "Int",
                "fieldname": "calorie_count",
                change() {
                    const { nutritional_plan } = dialog.fields_dict;
                    nutritional_plan.set_value("");
                }
            },
            {
                "label": __("Select Nutritional Plan"),
                "fieldtype": "Section Break",
            },
            {
                "label": __("Nutritional Plan"),
                "fieldtype": "Link",
                "fieldname": "nutritional_plan",
                "options": "Nutritional Plan",
                "reqd": 1,
                get_query() {
                    const { purpose, calorie_count } = dialog.fields_dict;

                    const filters = {
                        "purpose": purpose.value,
                    }

                    const is_calorie_count_empty = [
                        null,
                        undefined,
                        0
                    ].includes(calorie_count.value);

                    if (!is_calorie_count_empty) {
                        filters.calorie_count = calorie_count.value;
                    }
                    return { filters }
                }
            },
        ]
        const primary_action_label = __("Send Nutritional Plan");
        const primary_action = (values) => {
            const label = __(`Se le enviará el plan nutricional al paciente ${frm.doc.patient}`)
                + "<br><br>"
                + __("¿Está seguro que desea continuar?");

            const on_confirm = () => {
                const nutritional_plan = values.nutritional_plan;

                if (nutritional_plan) {
                    frappe.call({
                        method: "real_fitness.controllers.patient_encounter.patient_encounter.send_nutritional_plan",
                        args: {
                            patient_encounter: frm.doc.name,
                            nutritional_plan,
                            patient: frm.doc.patient,
                        },
                    });
                }
            }

            frappe.confirm(label, on_confirm);
            dialog.hide();
        }

        let dialog = new frappe.ui.Dialog({
            title,
            fields,
            primary_action_label,
            primary_action,
        });

        dialog.show();


    }

    frappe.ui.form.on("Patient Encounter", {
        refresh,
    });
}