# Copyright (c) 2023, Miguel Higuera and contributors
# For license information, please see license.txt

import re

import frappe

from frappe import _


@frappe.whitelist()
def send_nutritional_plan(patient_encounter, nutritional_plan):
    _send_nutritrional_plan(patient_encounter, nutritional_plan)


def _send_nutritrional_plan(patient_encounter, nutritional_plan):
    doc = get_patient_encounter(patient_encounter)
    attachment_name = get_attachment_name(nutritional_plan)

    email = get_patient_email(doc.patient)
    subject = f"Plan Nutricional para {doc.patient_name}"
    template = "nutritional_plan"
    args = {
        "name": doc.name,
        "patient_name": doc.patient_name,
    }

    site_path = frappe.utils.get_site_path()
    attachments = [get_attachment(
        get_filename_for_document(nutritional_plan, attachment_name), f"{site_path}/{attachment_name}")]

    frappe.sendmail(
        recipients=email,
        subject=subject,
        template=template,
        args=args,
        attachments=attachments,
    )

    frappe.msgprint(_("Nutritional Plan sent to Patient"))


def get_patient_encounter(patient_encounter):
    doctype = "Patient Encounter"

    doc = frappe.get_doc(doctype, patient_encounter)

    return doc


def get_attachment_name(nutritional_plan):
    doctype = "Nutritional Plan"

    doc = frappe.get_doc(doctype, nutritional_plan)

    return doc.document


def get_patient_email(patient):
    doctype = "Patient"

    try:
        patient = frappe.get_doc(doctype, patient)
    except Exception:
        frappe.throw(_("Patient not found"))
    else:
        email = patient.email

        if email:
            email = [e.strip() for e in email.split(",")]
        else:
            frappe.throw(_("Patient does not have an email"))

        return email


def get_attachment(filename, fileurl):
    with open(fileurl, "rb") as f:
        filecontent = f.read()

        return {
            "fname": filename,
            "fcontent": filecontent,
        }


def get_filename_for_document(patient_encounter, filepath):
    """Returns a valid filename for the given document and filepath."""

    # the idea here is to use the docname as the sanitized filename
    # and append the extension from the filepath

    # filename = frappe.scrub(docname)
    # scrubbing might not do the job, becuase it does not remove special characters
    # like /, |, #, etc. which might not be valid in filenames.

    special_characters = [
        "/", "\\", "|", "#", "?", "*", ":", "<", ">", "@", "!",
        "=", "[", "]", "{", "}", "'", "(", ")", "&", "$", ";",
        "+", "%", ",", '"', "`", "~", "^", " ", "\t", "\n", "\r",
    ]

    # now replace all special characters with -
    filename = patient_encounter
    for character in special_characters:
        filename = filename.replace(character, "-")

    # now append the extension
    filename += "." + filepath.split(".")[-1]

    # leave only single dashes between words (remove repeated dashes)
    # let's remove them using regex
    filename = re.sub("-+", "-", filename)

    return filename.lower()


@frappe.whitelist()
def get_all_lab_tests(arg=None):
    """Return all Test Labs"""

    doctype = "Lab Test Template"

    return [d.name for d in frappe.get_all(doctype, fields=["name"])]

