"""Python controller for DocType > Verify Pro"""

# Copyright (c) 2024, Rainier J Polanco and contributors
# For license information, please see license.txt

from typing import Optional, Union
from datetime import datetime
import random


import frappe
from frappe import utils
from frappe.model.document import Document


class VerifyPro(Document): # pylint: disable=missing-class-docstring
    def before_insert(self): # pylint: disable=missing-function-docstring
        if self.auto_generate:
            self.generate_code()

    def after_insert(self): # pylint: disable=missing-function-docstring
        self.set_title()

    def after_save(self): # pylint: disable=missing-function-docstring
        if not self.authorization_code:
            self.authorization_code = None

    def on_update(self): # pylint: disable=missing-function-docstring
        self.queue_action("disable_other_codes")

    @frappe.whitelist()
    def generate_code(self, force=False) -> None:
        """Get and set a new code."""
        if self.authorization_code:
            if not force:
                frappe.throw("This document already has a code.")

        authorization_code = self.get_new_code()

        if authorization_code:
            self.db_set("authorization_code", authorization_code)

    def get_new_code(self) -> int:
        """Return a new generate random code."""
        if not self.auto_generate:
            return # if auto_generate is not checked, do nothing

        _authorization_code = random.randint(
            self.get_min_code(), self.get_max_code()
        )

        if _authorization_code in self.get_used_codes():
            # keep generating until we get a unique code
            return self.get_new_code()
        
        return _authorization_code
    
    def get_min_code(self) -> int:
        """Get the minimum code."""
        return 10 ** (self.code_length - 1)
    
    def get_max_code(self) -> int:
        """Get the maximum code."""
        return 10 ** self.code_length - 1

    def set_title(self):
        """Set the title."""
        self.db_set("title", f"VERIFY-PRO-{self.name:04}")


    def disable_other_codes(self):
        """Disable other codes."""
        frappe.db.sql(
            f"""
            UPDATE
                `tabVerify Pro`
            SET
                enabled = 0,
                status = "Disabled",
                modified = {frappe.utils.now()!r}
            WHERE
                name != {self.name}
                AND user = {self.user!r}
            """
        )

    def get_used_codes(self):
        """Get all used codes."""

        used_codes_key = "_used_codes"

        if not hasattr(self, used_codes_key):
            used_codes = set(
                frappe.db.sql_list(
                    """
                    SELECT
                        authorization_code
                    FROM
                        `tabVerify Pro`
                    """
                )
            )

            setattr(self, used_codes_key, used_codes)

        return getattr(self, used_codes_key)
    

    def expire_code(self):
        """
        Expire the verification code if it has passed the expiration date.

        This method checks if the code expiration date is earlier than the current datetime.
        If it is, the status of the verification code is set to "Expired" in the database.
        """
        if not self.enabled:
            frappe.throw("Verify Pro is already disabled, hence not need to expire it")

        today = utils.getdate(
            utils.today()
        )

        expiration_date = utils.getdate(
            self.code_expiration
        )

        if today > expiration_date:
            self.status = "Expired"
            self.enabled = False
            self.modified = utils.now()
            self.db_update()


    code_expiration: Union[str, datetime, None]
    code_length: int = 4
    authorization_code: int
    user: str
    title: str
    amended_from: Optional[str]
    auto_generate: bool = True
