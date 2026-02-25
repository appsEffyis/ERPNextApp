# LodinPay Integration for ERPNext

Cette application permet d'intégrer la passerelle de paiement **LodinPay** au sein d'ERPNext v15. Elle automatise la génération de liens de paiement sécurisés et la synchronisation des statuts de facturation.

## Fonctionnalités principales

- 🔗 **Génération automatique de liens RTP** (Request To Pay) lors de la soumission d'une facture.
- 📄 **Synchronisation des PDF** : Envoi automatique de la facture au format PDF vers le backend LodinPay.
- 📱 **QR Code dynamique** : Affichage d'un QR Code carré sur la facture pour un paiement mobile instantané.
- 🔄 **Vérification en temps réel** : Bouton de synchronisation pour mettre à jour le statut de la facture (`Unpaid` ⮕ `Paid`) dès que le paiement est confirmé.
- 🛡️ **Sécurité** : Signature des transactions via HMAC-SHA256.

## Installation

Vous pouvez installer cette application en utilisant la CLI [bench](https://github.com/frappe/bench) :

```bash
cd frappe-bench
bench get-app https://github.com/appsEffyis/ERPNextApp.git --branch app
bench --site [votre-site] install-app lodin
bench --site [votre-site] migrate