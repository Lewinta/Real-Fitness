import frappe

def validate(doc, method):
    copy_cost_center_from_parent(doc)

def copy_cost_center_from_parent(doc):
    for item in doc.items:
        item.cost_center = doc.cost_center

