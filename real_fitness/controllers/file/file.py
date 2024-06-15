import frappe
from datetime import datetime

def validate(doc, method):
    if not doc.attached_to_doctype == "Patient":
        return

    formato_incorrecto = datetime.strptime(doc.creation, '%Y-%m-%d %H:%M:%S.%f')
    formato_correcto = formato_incorrecto.strftime('%d-%m-%Y')
    doc.file_name = formato_correcto
    # if doc.file_url:
    #     file_url = f"/".join(doc.file_url.split("/")[:-1])
    #     new_file_url = f"{file_url}/{doc.creation.split(' ')[0]}.{doc.file_type.lower()}"
    #     doc.file_url = new_file_url
        