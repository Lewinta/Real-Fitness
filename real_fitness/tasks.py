# Copyright (c) 2023, Yefri Tavarez and Contributors
# For license information, please see license.txt


import frappe


def all():
    ...


def daily():
    queue = "default"
    tasks = (
        ("real_fitness.controllers.automation.verify_pro.mark_as_expired_verify_pros", "Mark as Expired Verify Pros"),
    )

    for method, job_name in tasks:
        frappe.enqueue(
            method=method,
            queue=queue,
            job_name=job_name,
        )


def hourly():
    ...


def weekly():
    ...


def monthly():
    ...

