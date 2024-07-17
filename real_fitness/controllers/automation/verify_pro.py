# Copyright (c) 2024, Yefri Tavarez and Contributors
# For license information, please see license.txt

"""
This module contains functions for managing 'Verify Pro' records within
a Frappe application.

The primary functionality provided by this module is to mark
the so called 'Verify Pro' records as expired based on certain criteria.
It includes functions to identify such records and update their status accordingly.

Functions:
    mark_as_expired_verify_pros(): Marks all expired 'Verify Pro' records as
    expired by updating their status.
    get_all_expired_records(): Retrieves a list of all 'Verify Pro' records 
    that are considered expired based on their expiration date and current status.
"""


import frappe


__all__ = (
    "mark_as_expired_verify_pros",
)


def mark_as_expired_verify_pros():
    """
    Marks the 'Verify Pro' records as expired.

    This function retrieves all the expired 'Verify Pro' records and marks them as expired
    by calling the `expire_code` method on each record.

    Parameters:
        None

    Returns:
        None
    """
    doctype = "Verify Pro"
    for name in get_all_expired_records():
        doc = frappe.get_doc(doctype, name)

        doc.expire_code()


def get_all_expired_records():
    """
    Retrieve a list of all expired records from the 'Verify Pro' table.

    Returns:
        list: A list of expired record names.
    """
    return frappe.db.sql_list(
        """
            Select
                name
            From
                `tabVerify Pro`
            Where
                enabled = 1
                And status = "Active"
                And IfNull(code_expiration, CurDate()) < CurDate()
        """
    )
