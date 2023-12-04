
frappe.ui.form.on("POS Opening Shift", {
    refresh(frm) {
        frm.trigger("add_custom_buttons");
    },

    add_custom_buttons(frm) {
        frm.trigger("add_make_closing_button");
    },

    add_make_closing_button(frm) {
        if (frm.doc.docstatus != 1 || !frm.doc.status == "Closed") {
            return
        }

        frm.add_custom_button(__("Make Closing"), () => {
            frappe.call("posawesome.posawesome.doctype.pos_closing_shift.pos_closing_shift.make_closing_shift_from_opening",
                {
                    opening_shift: frm.doc
                }
            ).then(({ message }) => {
                frappe.new_doc("POS Closing Shift", message);
                // frappe.set_route("Form", "POS Closing Shift", message.name);
            });
        }).addClass("btn-primary");
    }

});