import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal

import frappe
import requests
from frappe import _
from frappe.utils import get_datetime, now_datetime, nowdate

RTP_API_URL = "https://api-preprod.lodinpay.com/merchant-service/extensions/pay/rtp"
INVOICE_API_URL = "https://api-preprod.lodinpay.com/merchant-service/extensions/invoices"
RTP_STATUS_API = "https://api-preprod.lodinpay.com/merchant-service/extensions/pay/rtp/check-status"
EXTENSION_CODE = "ERPNEXT"




# RTP GENERATION
def generate_rtp(doc, client_id, client_secret):

    invoice_id = doc.name.strip()

    # Normalized amount
    canonical_amount = (
        Decimal(str(doc.grand_total))
        .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        .to_eng_string()
    )


    timestamp = datetime.now(timezone.utc)\
        .isoformat(timespec="milliseconds")\
        .replace("+00:00", "Z")


    client_id = client_id.strip()
    client_secret = client_secret.strip()
    invoice_id = invoice_id.strip()


    payload = client_id + timestamp + canonical_amount + invoice_id
    signature = sign_payload(payload, client_secret)


    frappe.logger().info("=== DEBUG ===")
    frappe.logger().info(f"client_id  : '{client_id}'")
    frappe.logger().info(f"timestamp  : '{timestamp}'")
    frappe.logger().info(f"amount     : '{canonical_amount}'")
    frappe.logger().info(f"invoice_id : '{invoice_id}'")
    frappe.logger().info(f"payload    : '{payload}'")
    frappe.logger().info(f"signature  : '{signature}'")

    headers = {
        "Content-Type": "application/json",
        "X-Client-Id": client_id,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "X-Extension-Code": EXTENSION_CODE,
    }

    body = {
        "amount": float(canonical_amount),
        "invoiceId": invoice_id,
        "paymentType": "INST",
        "description": f"Invoice {invoice_id}",
    }

    r = requests.post(RTP_API_URL, json=body, headers=headers, timeout=20)

    if r.status_code != 200:
        frappe.logger().error(f"❌ RTP error {r.status_code}: {r.text}")
        frappe.throw(f"Failed to generate RTP: {r.text}")

    return r.json()



def send_invoice_to_backend(doc, client_id, client_secret, access_log_id):
    """Envoie les données de la facture à LodinPay"""
    invoice_number = doc.name.strip()

    items = []
    for line in doc.items:
        items.append({
            "name": line.item_name,
            "description": line.description or line.item_name,
            "unitPrice": float(line.rate),
            "quantity": float(line.qty),
            "totalPrice": float(line.amount),
        })

    body = {
            "externalInvoiceId": invoice_number,
            "invoiceNumber": invoice_number,
            "totalAmount": float(doc.grand_total),
            "taxAmount": float(doc.total_taxes_and_charges or 0.0),
            "feeAmount": 0.0,
            "currency": doc.currency,
            "description": f"ERPNext invoice {invoice_number}",
            "invoiceDate": now_datetime().replace(tzinfo=timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "accessLogId": access_log_id,
            "items": items
        }


    now = datetime.now(timezone.utc)
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    normalized_amount = (
        Decimal(str(doc.grand_total))
        .quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        .to_eng_string()
        )

    payload = client_id + timestamp + normalized_amount + invoice_number
    signature = sign_payload(payload, client_secret)

    headers = {
        "Content-Type": "application/json",
        "X-Client-Id": client_id,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "X-Extension-Code": EXTENSION_CODE,
    }

    try:
        r = requests.post(INVOICE_API_URL, json=body, headers=headers, timeout=30)

        if r.status_code in (200, 201):
            frappe.logger().info(f"Invoice {invoice_number} sent to LodinPay successfully !!")
            return r.json()


        frappe.logger().error(f"Invoice API error {r.status_code}: {r.text}")

        try:
            error_data = r.json()
            error_msg = error_data.get("message") or error_data.get("error") or r.text
        except Exception:
            error_msg = r.text

        # ✅ Si la facture existe déjà, on retourne None silencieusement
        if "already exists" in error_msg.lower():
            frappe.logger().info(f"Invoice {invoice_number} already exists on LodinPay, skipping silently.")
            return None

        frappe.throw(f"LodinPay API Error ({r.status_code}): {error_msg}")

    except requests.exceptions.RequestException as e:
        frappe.logger().exception(f" Request failed for invoice {invoice_number}")
        frappe.throw(f"Failed to connect to LodinPay: {e!s}")

    return None


def send_invoice_pdf_to_backend(doc, backend_invoice_id):

    # Credentials
    client_id = frappe.db.get_single_value("LodinPay Settings", "client_id")
    client_secret = frappe.db.get_single_value("LodinPay Settings", "client_secret")
    if not client_id or not client_secret:
        frappe.throw(_("LodinPay credentials are not configured. Please set them in LodinPay Settings."))


    if not backend_invoice_id or backend_invoice_id == "{invoiceId}":
        frappe.logger().error(f"❌ ID Backend invalide : {backend_invoice_id}")
        return False

    try:
        # PDF GENERATION
        frappe.logger().info(f"Generating PDF for invoice {doc.name}...")

        pdf_bytes = frappe.get_print(
            "Sales Invoice",
            doc.name,
            print_format="LodinPay Invoice Format",
            as_pdf=True,
            letterhead=True
        )

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        frappe.logger().info(f"PDF encodé ({len(pdf_base64)} caractères)")

        size_kb = len(pdf_base64) / 1024
        frappe.logger().info(f"PDF Taille Base64: {size_kb:.2f} KB")

        if size_kb > 1000: # Si plus de 1Mo
            frappe.logger().warning("Le PDF est encore trop lourd pour LodinPay ?!!")

    except Exception as e:
        frappe.logger().error(f"Erreur génération PDF : {e!s}")
        return False




    body = {
        "fileName": f"Invoice_{doc.name}.pdf",
        "base64Pdf": pdf_base64
    }


    external_invoice_id = doc.name.strip()
    normalized_amount = f"{float(doc.grand_total):.2f}"
    timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    payload = client_id.strip() + timestamp + normalized_amount + external_invoice_id
    signature = sign_payload(payload, client_secret.strip())

    headers = {
        "Content-Type": "application/json",
        "X-Client-Id": client_id.strip(),
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "X-Extension-Code": "ERPNEXT",
    }


    # Api call
    url = f"{INVOICE_API_URL}/{backend_invoice_id}/pdf"

    # Time delay to ensure LodinPay backend has processed the invoice data before receiving the PDF
    time.sleep(1)

    frappe.logger().info(f"Sending PDF to LodinPay for invoice {doc.name} (backend ID: {backend_invoice_id})...")

    try:
        r = requests.post(url, json=body, headers=headers, timeout=60)

        if r.status_code in (200, 201):
            frappe.logger().info(f"PDF for invoice {doc.name} sent to LodinPay successfully !!")
            return True

        frappe.logger().error(f"PDF API error {r.status_code}: {r.text}")
    except requests.exceptions.RequestException:
        frappe.logger().exception(f"Failed to send PDF for invoice {doc.name} to LodinPay")

    return False


# Sync invoice status with LodinPay
@frappe.whitelist()
def action_lodinpay_sync_status(invoice_names: str | list):
    if isinstance(invoice_names, str):
        invoice_names = json.loads(invoice_names)

    # Credentials
    client_id = frappe.db.get_single_value("LodinPay Settings", "client_id")
    client_secret = frappe.db.get_single_value("LodinPay Settings", "client_secret")

    if not client_id or not client_secret:
        frappe.throw(_("LodinPay credentials are not configured. Please set them in LodinPay Settings."))

    for invoice_name in invoice_names:
        try:
            doc = frappe.get_doc("Sales Invoice", invoice_name)

            if not doc.lodinpay_order_id:
                frappe.log_error(f"Invoice {invoice_name} has no LodinPay Order ID.", "LodinPay Sync Status")
                continue

            if doc.status == "Paid":
                frappe.log_error(f"Invoice {invoice_name} already marked as Paid.", "LodinPay Sync Status")
                continue

            # Signature
            now = datetime.now(timezone.utc)
            timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
            payload = client_id + timestamp + "0.00" + doc.lodinpay_order_id
            signature = sign_payload(payload, client_secret)

            headers = {
                "Content-Type": "application/json",
                "X-Client-Id": client_id,
                "X-Timestamp": timestamp,
                "X-Signature": signature,
                "X-Extension-Code": EXTENSION_CODE,
            }

            # API call
            r = requests.post(
                RTP_STATUS_API,
                json={"orderId": doc.lodinpay_order_id},
                headers=headers,
                timeout=20
            )

            if r.status_code != 200:
                try:
                    error_msg = r.json().get("message") or r.text
                except Exception:
                    error_msg = r.text

                frappe.log_error(f"Invoice {invoice_name}: API Error {r.status_code} - {error_msg}", "LodinPay Sync Status")
                continue

            # Response handling
            payment_status = r.json().get("status")
            frappe.logger().info(f"Status for invoice {invoice_name} (LodinPay Order ID: {doc.lodinpay_order_id}): {payment_status}")

            if payment_status == "Completed":
                mark_invoice_paid(doc)
                frappe.logger().info(f"Invoice {invoice_name} updated to Paid based on LodinPay status.")
            else:
                frappe.logger().info(f"Invoice {invoice_name} not updated. Payment status from LodinPay: {payment_status}")

        except Exception:
            frappe.logger().exception(f"Error syncing status for invoice {invoice_name}")

            continue

        frappe.db.commit() # nosemgrep - required after custom field installation

    return True


# Mark invoice as paid
def mark_invoice_paid(doc):

    if doc.status == "Paid":
        return

    journal = frappe.db.get_value(
        "Account",
        filters={
            "account_type": "Bank",
            "company": doc.company,
            "is_group": 0
        },
    )

    if not journal:
        frappe.throw(_("No bank account found..."))

     # Create Payment Entry to reconcile invoice once LodinPay confirms payment
    payment = frappe.get_doc({
            "doctype": "Payment Entry",
            "payment_type": "Receive",              # "inbound"
            "party_type": "Customer",               # "customer"
            "party": doc.customer,                  # partner_id
            "paid_amount": doc.grand_total,         # amount
            "received_amount": doc.grand_total,     # amount
            "posting_date": nowdate(),              # date
            "paid_from": doc.debit_to,              # Compte client
            "paid_to": journal,                     # journal_id (compte banque)
            "reference_no": f"LodinPay {doc.name}", # ref
            "reference_date": nowdate(),
            "company": doc.company,
            "references": [
                {
                    "reference_doctype": "Sales Invoice",
                    "reference_name": doc.name,
                    "total_amount": doc.grand_total,
                    "outstanding_amount": doc.outstanding_amount,
                    "allocated_amount": doc.grand_total
                }
            ]
        })
    payment.insert()
    payment.submit()

    frappe.db.commit() # nosemgrep - required after custom field installation
    frappe.logger().info(f"Invoice {doc.name} marked PAID")


# Sync invoice status with LodinPay
def sign_payload(payload, secret):
    """Signe le payload avec HMAC-SHA256"""
    raw_hmac = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()

    return base64.b64encode(raw_hmac).decode("utf-8").replace("+", "-").replace("/", "_").rstrip("=")


# Handle API error responses and extract meaningful message (NOTE: not currently used, but can be used in the future for better error handling)
def raise_backend_error(response, default_msg):
    """Gère les erreurs API de façon intelligente"""
    try:
        data = response.json()
        msg = data.get("message") or data.get("error") or data.get("detail") or response.text
    except Exception:
        msg = response.text or default_msg

    frappe.throw(f"LodinPay error ({response.status_code}): {msg}")
