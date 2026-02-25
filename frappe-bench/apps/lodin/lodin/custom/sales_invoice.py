"""
Sales Invoice hook for LodinPay integration.
Equivalent to Odoo's action_post() method.
"""


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
        
        
        if not doc.lodinpay_order_id:
            rtp_data = generate_rtp(doc, client_id, client_secret)
            
            
            doc.db_set('rtp_payment_link', rtp_data.get("url"), update_modified=False)
            doc.db_set('lodinpay_order_id', str(rtp_data.get("orderId")), update_modified=False)
            
            # TRÈS IMPORTANT : On valide l'écriture en base maintenant
            # Comme ça, même si le PDF plante, l'ID est sauvé !
            frappe.db.commit()
            
            access_log_id = rtp_data.get("accessLogId")
        else:
            # Si l'ID existe déjà, on ne veut pas renvoyer le JSON/PDF 
            # pour éviter les erreurs "Already exists" sur LodinPay
            frappe.logger().info(f"LodinPay already processed for {doc.name}")
            return

        # 2️⃣ ENVOIE DES DONNÉES JSON
        # On utilise 'access_log_id' défini dans le bloc au-dessus
        invoice_response = send_invoice_to_backend(
            doc, 
            client_id, 
            client_secret, 
            access_log_id
        )
        
        if "id" not in invoice_response:
            frappe.throw("LodinPay did not return an invoice id")
        
        backend_invoice_id = invoice_response["id"]

        # 3️⃣ ENVOIE DU PDF
        send_invoice_pdf_to_backend(doc, backend_invoice_id)
        
        frappe.logger().info(f"✅ LODINPAY FULL SYNC DONE invoice={doc.name}")
        
    except Exception as e:
        frappe.logger().exception(f"LodinPay process failed for invoice {doc.name}")
        # On affiche l'erreur mais on ne bloque pas forcément si l'ID est déjà généré
        frappe.msgprint(f"Erreur LodinPay: {str(e)}", indicator="red")