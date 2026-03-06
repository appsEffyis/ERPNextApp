"""
Installation of custom fields for LodinPay
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def install():
    """
    Crée les custom fields au démarrage de l'app
    Appelé automatiquement par le hook after_install
    """
    custom_fields = {
        "Sales Invoice": [
            {
                "fieldname": "rtp_payment_link",
                "label": "Lien de paiement RTP",
                "fieldtype": "Data",
                "insert_after": "grand_total",
                "read_only": 1,
                "no_copy": 1,
                "print_hide": 1,
            },
            {
                "fieldname": "lodinpay_order_id",
                "label": "LodinPay Order ID",
                "fieldtype": "Data",
                "insert_after": "rtp_payment_link",
                "read_only": 1,
                "no_copy": 1,
                "print_hide": 1,
            }
        ]
    }

    create_custom_fields(custom_fields, update=True)
    set_default_print_format()
    frappe.db.commit() # nosemgrep - required after custom field installation

    print("✅ LodinPay custom fields created successfully!")


def set_default_print_format():
    """Définit LodinPay Invoice Format comme format par défaut pour Sales Invoice"""
    frappe.db.set_value("DocType", "Sales Invoice", "default_print_format", "LodinPay Invoice Format")
    frappe.db.commit() # nosemgrep - required after custom field installation
    print("✅ LodinPay Invoice Format est maintenant le format par défaut.")
