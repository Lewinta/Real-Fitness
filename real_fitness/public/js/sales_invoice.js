{
    function refresh(frm) {
        frappe.run_serially([
            () => hide_custom_buttons(frm),
            () => add_custom_buttons(frm),
            () => set_values(frm),
        ]);
    }

    function before_submit(frm) {
        return new Promise((resolve, reject) => {
            confirm_permission(frm, resolve, reject);
        });
    }

    function hide_custom_buttons(frm) {
        hide_healthcare_services_button(frm);
    }

    function add_custom_buttons(frm) {
        add_healthcare_services_button(frm);
    }

    function hide_healthcare_services_button(frm) {
        setTimeout(() => {
            frm.remove_custom_button("Healthcare Services", __("Get Items From"));
        }, 1000);
    }

    function add_healthcare_services_button(frm) {
        const label = "Patient Encounter";
        const action = () => {
            multiselect_dialog_for_patient_encounter(frm);
        };
        const group = __("Get Items From");

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

    function set_values(frm) {
        frappe.run_serially([
            () => set_outstanding_amount(frm),
            () => set_paid_amount(frm),
            () => set_change(frm),
        ]);
    }

    function set_outstanding_amount(frm) {        
        const { doc } = frm;
        frm.set_value("outstanding_amount_copy", doc.grand_total);        
    }

    function set_paid_amount(frm) {
        const { doc } = frm;
        let total_paid_amount = 0;

        if (doc.payments){
            doc.payments.forEach(row => {
                if(row.type == "Cash"){
                    total_paid_amount += row.amount;                    
                }            
            });
            frm.set_value("paid_amount_copy", total_paid_amount);
        }
    }

    function set_change(frm) {
        const { doc } = frm;
        frm.set_value("change",doc.paid_amount_copy -  doc.outstanding_amount_copy);
    }

    function amount(frm) {
        set_values(frm);        
    }

    // Validar si el usuario actual tiene permisos para realizar la operacion
    // Validar si la factura es de credito
    function confirm_permission(frm, resolve, reject){
        frappe.call({
            method: "real_fitness.controllers.sales_invoice.sales_invoice.confirm_actual_user_has_permission",
            callback: (response) => {
                const { message } = response;
                console.log("message.has_permission", message);
                if (frm.doc.outstanding_amount > 0){
                    show_dialog_to_confirm_permission(message, resolve, reject);
                } else {
                    resolve(); 
                }
            },
            error: function (error) {
                console.error("Error en confirm_permission:", error);
                reject(); 
            }
        });
    }

    function show_dialog_to_confirm_permission(has_permission, resolve, reject) {
        if (!has_permission) {
            create_dialog_to_confirm_permission(resolve, reject);
        } else {
            resolve(); 
        }
    }

    // Pedir al usuario actual que ingrse un usuario que si tenga permisos para realizar la operacion
    // validar si el usuario tiene permisos para realizar la operacion y si introduce la contraseña correcta
    function create_dialog_to_confirm_permission(resolve, reject) {
        const fields = [
            {
                fieldtype: "HTML",
                options: `<p>Por cuestiones de seguridad, se solicita la aprobación de un usuario con permisos para poder validar esta transacción. Por favor, introduzca los datos de un usuario con los permisos de validar facturas a crédito. ¡Gracias!</p>`
            },
            {
                label: "User",
                fieldname: "user",
                fieldtype: "Link",
                options: "User",
            },
            {
                label: "Password",
                fieldname: "password",
                fieldtype: "Password"
            },
        ];

        frappe.prompt(fields, (values) => {
            frappe.call({
                method: "real_fitness.controllers.sales_invoice.sales_invoice.validate_user_and_permission",
                args: {
                    user: values.user,
                    password: values.password,
                },
                callback: (response) => {
                    const { message } = response;
                    if (message) {
                        frappe.msgprint("Permiso concedido");
                        resolve(); 
                    } else {
                        frappe.throw("Permiso denegado");
                        reject(); 
                    }
                },
                error: function (error) {
                    console.error("Error en show_dialog_to_confirm_permission:", error);
                    reject(); 
                }
            });
        }).catch((error) => {
            console.error("Error en frappe.prompt:", error);
            reject(); 
        });
    }

    frappe.ui.form.on("Sales Invoice Payment", {
        amount,        
    });

    frappe.ui.form.on("Sales Invoice", {
        refresh,
        before_submit,
    });
}
