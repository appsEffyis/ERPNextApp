frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1 
            && frm.doc.lodinpay_order_id 
            && frm.doc.status !== 'Paid') {

            // On ajoute le bouton SANS le paramètre de groupe à la fin
            frm.add_custom_button(__('🔄 Sync LodinPay'), function() {
                frappe.call({
                    method: 'lodin.custom.lodinpay_integration.action_lodinpay_sync_status',
                    args: { invoice_names: JSON.stringify([frm.doc.name]) },
                    freeze: true,
                    freeze_message: 'Vérification en cours...',
                    callback: function(r) {
                        frappe.show_alert({ 
                            message: ' Sync terminée!', 
                            indicator: 'green' 
                        }, 3);
                        frm.reload_doc();
                    }
                });
            });


            frm.change_custom_button_type(__('🔄 Sync LodinPay'), null, 'primary');
        }
    }
});