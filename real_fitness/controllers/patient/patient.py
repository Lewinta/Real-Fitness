# Copyright (c) 2023, Miguel Higuera and contributors
# For license information, please see license.txt


import frappe

def validate(doc, method=None):
    validate_referrals(doc)


def validate_referrals(doc):
    # If referral type is customer or healthcare practitioner, 
    # then other referrer field should be blank

    referral_types = [
        "Customer", 
        "Healthcare Practitioner"
    ]

    if doc.referral_type in referral_types:
        doc.other_referrer = None
    
    if doc.referral_type == "Other" or None:
        doc.referrer = None