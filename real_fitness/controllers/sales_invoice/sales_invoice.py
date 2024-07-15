# Copyright (c) 2023, Yefri Tavarez and Contributors
# For license information, please see license.txt


import json
from typing import Union

import frappe
from frappe.utils.password import check_password

from erpnext.setup.utils import get_exchange_rate


CREDIT_CONTROLLER_ROLE = "Supervisor de Ventas"


def validate(doc, method=None):
    doc.posa_pos_opening_shift = validate_pos_entry(doc)


def before_submit(doc, method=None):
    validate_code_if_applies(doc)


def validate_code_if_applies(doc):
    if doc.outstanding_amount <= 0:
        # we're looking for invoices with outstanding amount
        return # do nothing if the amount is less than or equal to 0

    if CREDIT_CONTROLLER_ROLE in frappe.get_roles():
        return # do nothing and returns nothing if the user has the role

    if not doc.code:
        frappe.throw(
            "Código de autorización es requerido para facturas con saldo pendiente")

    if not confirm_if_user_made_a_verify_pro(doc.code):
        frappe.throw("Código de autorización incorrecto")


def validate_pos_entry(doc):
    # All previous Shifts must be closed beforeg starting the day
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


@frappe.whitelist()
def confirm_actual_user_has_permission():
    """
    Checks if the actual user has permission to perform the operation.

    Returns:
        bool: True if the user has permission, False otherwise.
    """

    return CREDIT_CONTROLLER_ROLE in frappe.get_roles()


@frappe.whitelist()
def validate_user_and_permission(user, password):
    """
    Validates the user's password and checks if the user has permission.

    Args:
        user (str): The username.
        password (str): The user's password.

    Returns:
        bool: True if the user has permission, False otherwise.
    """
    try:
        check_password(user, password)
    except Exception:
        frappe.throw("Contraseña incorrecta")

    has_permission = validate_user_permission(user)
    return has_permission


def validate_user_permission(user):
    """
    Check if the given user has the permission to perform sales invoice operations.

    Args:
        user (str): The name of the user to check permission for.

    Returns:
        bool: True if the user has the permission, False otherwise.
    """
    has_permission = False
    user_doc = frappe.get_doc("User", user)
    for role in user_doc.roles:
        if role.role == "Supervisor de Ventas":
            has_permission = True
            break
    return has_permission


@frappe.whitelist()
def confirm_if_user_made_a_verify_pro(code: Union[str, int]) -> bool:
    """
    Check if a user has made a Verify Pro with the given authorization code.

    Args:
        code (str): The authorization code to check.

    Returns:
        bool: True if a Verify Pro with the given authorization code and status "Active" exists, False otherwise.
    """
    if not code:
        return False

    return bool(
        frappe.db.exists("Verify Pro", {
            "authorization_code": code,
            "status": "Active"
        })
    )
