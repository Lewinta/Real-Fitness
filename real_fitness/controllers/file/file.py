# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

import re

import frappe
from datetime import datetime


def validate(doc, method):
    rename_filename_for_patients(doc)


def rename_filename_for_patients(doc):
    if not doc.attached_to_doctype == "Patient":
        return

    creation_object = frappe.utils.getdate(doc.creation)
    formatted_date = creation_object.strftime("%d.%m.%Y")

    current_count = get_current_count(
        formatted_date, doc.attached_to_doctype, doc.attached_to_name
    )

    # sets the file name to the format "dd.mm.yyyy (n)"
    doc.file_name = f"{formatted_date} ({int(current_count) + 1})"


def get_current_count(
    date_str: str, attached_to_doctype: str, attached_to_name: str
) -> str:
    """
    Get the current count of files attached to a document (used in Patient attachments)
    date_str: str -> The date string in the format "dd.mm.yyyy"
    attached_to_doctype: str -> The doctype of the document to which the file is attached
    attached_to_name: str -> The name of the document to which the file is attached

        Example -> 
            * 24.06.2018 (1)
            * 24.06.2018 (2)
            * 24.06.2018 (3)
    """
    [file_name] = frappe.db.sql_list(
        f"""
            Select
                Max(file.file_name) As file_name
            From
                `tabFile` As file
            Where
                file.attached_to_doctype = {attached_to_doctype!r}
                And file.attached_to_name = {attached_to_name!r}
                And file.file_name Like "{date_str}%%"
        """, as_list=False
    )

    if not file_name:
        return 0

    # extract the number from the file_name within the parenthesis
    match = re.search(r"\((\d+)\)", file_name)

    if match:
        current_count = match.group(1)
        return current_count

    # if no match is found, return 0 for the first file of the day
    return 0
