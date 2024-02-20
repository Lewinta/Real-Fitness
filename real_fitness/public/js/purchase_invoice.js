frappe.ui.form.on("Purchase Invoice", {
    cost_center: function(frm) {
        frm.doc.items.forEach((item) => {
            item.cost_center = frm.doc.cost_center;
        });

        frm.refresh_field("items");
    }
});
