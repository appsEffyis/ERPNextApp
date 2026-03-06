# LodinPay Integration for ERPNext

Cette application permet d'intégrer la passerelle de paiement **LodinPay** au sein d'ERPNext v15. Elle automatise la génération de liens de paiement sécurisés et la synchronisation des statuts de facturation.

## 🔗 Fonctionnalités principales

- **Génération automatique de liens RTP** (Request To Pay) lors de la soumission d'une facture.
- 📄 **Synchronisation des PDF** : Envoi automatique de la facture au format PDF vers le backend LodinPay.
- 📱 **QR Code dynamique** : Affichage d'un QR Code carré sur la facture pour un paiement mobile instantané.
- 🔄 **Vérification en temps réel** : Bouton de synchronisation pour mettre à jour le statut de la facture (`Unpaid` ⮕ `Paid`) dès que le paiement est confirmé.
- 🛡️ **Sécurité** : Signature des transactions.

## ⚙️ Prérequis

Avant d'installer l'application, vous devez :
1. Créer un compte sur [LodinPay Merchant Portal](https://merchant.lodinpay.com/auth/login).
2. Récupérer vos identifiants : **Client ID** et **Client Secret**.
3. S'assurer que le site ERPNext est configuré pour accepter la devise **EUR** (seule devise supportée par l'intégration).

