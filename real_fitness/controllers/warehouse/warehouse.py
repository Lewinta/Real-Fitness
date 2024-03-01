# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe

from erpnext.stock.doctype.warehouse import warehouse

class Warehouse(warehouse.Warehouse):
    def on_update(self):
        super(Warehouse, self).on_update()

        self.create_user_permissions_if_applies()

    def create_user_permissions_if_applies(self):
        """When does it apply? When the warehouse_staff has been changed.
        So, let's check that first.
        """

        before_save = self.get_doc_before_save()

        if not before_save:
            return self.create_user_permissions()

        # if before_save.warehouse_staff != self.warehouse_staff:
        # would be as simple as this if it works, but it doesn't work
        # because everytime the user saves the document, a new array is created
        # and the comparison will always be false

        # so, we need to compare the user list manually
        # and that's what we're going to do next

        previous_users = {
            (user.user, user.privileges) for user in before_save.warehouse_staff
        }
        current_users = {
            (user.user, user.privileges) for user in self.warehouse_staff
        }

        if previous_users != current_users:
            self.update_user_permissions()

    def update_user_permissions(self):
        """Update user permissions for the warehouse staff"""
        self.remove_user_permissions()
        self.create_user_permissions()

    def remove_user_permissions(self):
        """Remove user permissions for the warehouse staff"""
        
        doctype = "User Permission"
        filters = {
            "allow": "Warehouse",
            "for_value": self.name,
        }

        pluck = "name"

        for name in frappe.get_all(doctype, filters=filters, pluck=pluck):
            frappe.delete_doc(doctype, name)

    def create_user_permissions(self):
        """Create user permissions for the warehouse staff"""
        for staff in self.warehouse_staff:
            # Is the staff privileged?
            is_default = not staff.privileges == "Privileged"

            get_user_permission(staff.user, self.name, is_default) \
                .insert()

        if not self.default_in_transit_warehouse:
            frappe.throw(
                "Please set a default in transit warehouse for this warehouse"
            )

        get_user_permission(staff.user, self.default_in_transit_warehouse, False) \
            .insert()

def get_user_permission(user, warehouse, is_default):
    doc = frappe.new_doc("User Permission")

    doc.update({
        "is_default": is_default,
        "apply_to_all_doctypes": 1,
        "hide_descendants": 0,
        "user": user,
        "allow": "Warehouse",
        "for_value": warehouse
    })

    doc.flags.ignore_permissions = True
    doc.flags.ignore_mandatory = True

    return doc