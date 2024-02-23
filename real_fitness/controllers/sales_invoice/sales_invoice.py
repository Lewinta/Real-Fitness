# Copyright (c) 2023, Yefri Tavarez and Contributors
# For license information, please see license.txt

import frappe
import json
from erpnext.setup.utils import get_exchange_rate


def validate(doc, method):
    entry = validate_pos_entry(doc)
    doc.posa_pos_opening_shift = entry


def validate_pos_entry(doc):
    # All previous Shifts must be closed before starting the day
    filters = {
        "docstatus": 1,
        "status": "Open",
        "posting_date": ["<", doc.posting_date]
    }
    open_shifts = frappe.get_list("POS Opening Shift", filters, [
                                  'name', 'posting_date'])
    if open_shifts:
        # show a message with the open shifts
        frappe.throw(f"""
            Favor cerrar las siguientes aperturas de caja antes de continuar:
            <ul>
                {"".join([f"<li>{x.name} - {x.posting_date}</li>" for x in open_shifts])}
            </ul>
        """)

    # We have to make sure there is a opening shift before creating an invoice
    entry = get_opening_entry(doc)
    if not entry:
        dt = frappe.format_value(doc.posting_date, {"fieldtype": "Date"})
        frappe.throw(f"""
            Favor hacer la apertura de caja para <b>{doc.pos_profile}</b> con fecha de <b>{dt}</b>
        """)
    else:
        return entry


def get_opening_entry(doc):
    if not doc.pos_profile:
        return True

    filters = {
        "docstatus": 1,
        "status": "Open",
        "posting_date": doc.posting_date,
        "pos_profile": doc.pos_profile
    }

    return frappe.db.exists("POS Opening Shift", filters)


@frappe.whitelist()
def get_items_from_patient_encounter_in_clinical_procedure(selections):
    patient_encounters = json.loads(selections)
    doctype = "Patient Encounter"
    default_currency = frappe.defaults.get_global_default("currency")
    items = []

    for patient_encounter in patient_encounters:
        patient_encounter = frappe.get_doc(doctype, patient_encounter)

        # procedure_prescription is the table that contains the procedures
        if not patient_encounter.procedure_prescription:
            continue

        for procedure in patient_encounter.procedure_prescription:
            item = get_item_for_procedure(procedure.procedure)

            if not item:
                continue

            if procedure.currency != default_currency:
                rate = get_exchange_rate(procedure.currency, default_currency)

                if rate:
                    procedure.amount = procedure.amount * rate

            items.append({
                "item_code": item.item_code,
                "rate": procedure.amount,
                "qty": 1,
                "currency": procedure.currency,
            })

    return items


def get_item_for_procedure(procedure):
    doctype = "Item"
    name = procedure

    if not frappe.db.exists(doctype, name):
        return None

    return frappe.get_doc(doctype, name)
