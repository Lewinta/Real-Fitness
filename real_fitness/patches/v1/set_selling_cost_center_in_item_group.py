import frappe


def execute():
    set_selling_cost_center_in_item_group()


def set_selling_cost_center_in_item_group():
    item_groups = get_item_groups()

    for item_group in item_groups:
        doc = frappe.get_doc("Item Group", item_group.name)

        if not doc.item_group_defaults:
            item_group_values = {
                "company": "Real Fitness",
                "selling_cost_center": "General - RF"
            }

            doc.append("item_group_defaults", item_group_values)
            doc.save()

            print(f"Item Group {item_group.name} updated")


def get_item_groups():
    doctype = "Item Group"
    fields = ["name"]

    return frappe.get_all(doctype, fields)
