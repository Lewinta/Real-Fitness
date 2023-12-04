// Copyright (c) 2023, Miguel Higuera and contributors
// For license information, please see license.txt

frappe.ui.form.on("Patient", {
    refresh(frm) {
        frm.trigger("set_intro_for_viral_condition");
    },

    referral_type(frm) {
        const { doc } = frm;

        if (doc.referral_type == "Other") {
            frm.set_value("referrer", null);
        }

        if (doc.referral_type == "Customer" || doc.referral_type == "Healthcare Practitioner") {
            frm.set_value("other_referrer", null);
        }

        if (doc.referral_type == "") {
            frm.set_value("referrer", null);
            frm.set_value("other_referrer", null);
        }
    },

    set_intro_for_viral_condition(frm) {
        const { doc } = frm;

        if (doc.viral_condition) {
            frm.set_intro(
                `<i class='fa fa-exclamation-triangle' style='color:red'></i> Paciente con virus de <b>${frm.doc.viral_condition}</b>`,
                'red'
            );
        }
    },
});