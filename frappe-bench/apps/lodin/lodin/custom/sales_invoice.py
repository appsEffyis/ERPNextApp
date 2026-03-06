import frappe

def on_submit(doc, method):
    if doc.currency != "EUR":
        frappe.msgprint(
            msg=f"LodinPay skipped for invoice {doc.name} (LodinPay uses only EUR, not {doc.currency})",
            alert=True,
            indicator="orange"
        )
        return

    from lodin.custom.lodinpay_integration import (
        generate_rtp,
        send_invoice_to_backend,
        send_invoice_pdf_to_backend
    )

    client_id = frappe.db.get_single_value("LodinPay Settings", "client_id")
    client_secret = frappe.db.get_single_value("LodinPay Settings", "client_secret")

    if not client_id or not client_secret:
        frappe.logger().error("Missing LodinPay credentials")
        return

    try:
        frappe.logger().info(f"===== LODINPAY PROCESS START invoice={doc.name} =====")

        # ✅ Double check en base au cas où doc en mémoire n'est pas à jour
        lodinpay_order_id = frappe.db.get_value("Sales Invoice", doc.name, "lodinpay_order_id")

        if lodinpay_order_id:
            frappe.logger().info(f"LodinPay already processed for {doc.name}")
            return

        # 1️⃣ GÉNÉRATION DU RTP
        access_log_id = None
        try:
            rtp_data = generate_rtp(doc, client_id, client_secret)
            doc.db_set('rtp_payment_link', rtp_data.get("url"), update_modified=False)
            doc.db_set('lodinpay_order_id', str(rtp_data.get("orderId")), update_modified=False)
            frappe.db.commit()
            access_log_id = rtp_data.get("accessLogId")
        except Exception as e:
            if "already exists" in str(e).lower():
                frappe.logger().info(f"RTP already exists for {doc.name}, skipping silently.")
                return  # ✅ Sort proprement sans message d'erreur
            raise e

# 2️⃣ ENVOI DES DONNÉES JSON
        backend_invoice_id = None
        try:
            invoice_response = send_invoice_to_backend(doc, client_id, client_secret, access_log_id)
            backend_invoice_id = invoice_response.get("id") if invoice_response else None
        except (Exception, frappe.ValidationError) as e:
            if "already exists" in str(e).lower():
                frappe.logger().info(f"Invoice {doc.name} already exists on LodinPay, skipping.")
            else:
                raise e

        # 3️⃣ ENVOI DU PDF
        if backend_invoice_id:
            send_invoice_pdf_to_backend(doc, backend_invoice_id)
            frappe.logger().info(f"✅ LODINPAY FULL SYNC DONE invoice={doc.name}")
        else:
            frappe.logger().warning(f"⚠️ PDF sync skipped: No backend_invoice_id for {doc.name}")

    except (Exception, frappe.ValidationError) as e:
        frappe.logger().exception(f"LodinPay process failed for invoice {doc.name}")
        if "already exists" not in str(e).lower():
            frappe.msgprint(f"Erreur LodinPay: {str(e)}", indicator="red")