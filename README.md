# Site Chaïda Trust + back-office de gestion

Site vitrine multi-pages pour Chaïda Trust (phytothérapie/cosmétologie, création
de mode, esthétique, marketing digital, formation), avec formulaires de
réservation de programme/rendez-vous, d'inscription aux formations et de
contact — tous reliés à un back-office pour suivre les demandes.

## Démarrage rapide (en local)

```bash
python3 -m venv venv
source venv/bin/activate          # sous Windows : venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env              # puis remplir les valeurs

python3 init_db.py                # crée la base + admin + les 5 activités
python3 run.py                    # lance le serveur sur http://localhost:5000
```

Compte admin par défaut créé par `init_db.py` :
- email : `admin@chaidatrust.com`
- mot de passe : `changez-ce-mot-de-passe` (**à changer immédiatement**)

Back-office accessible sur `/admin/login`.

## Pages du site public

- **Accueil** (`/`) — présentation, pourquoi choisir Chaïda Trust, vision
- **Nos activités** (`/services`) — les 5 domaines, chacun avec un bouton vers sa page dédiée
- **Page activité** (`/service/<slug>`) — détail + formulaire de réservation de programme/RDV
- **Formations** (`/formations`) — domaines de formation + formulaire d'inscription
- **Contact** (`/contact`) — coordonnées, réseaux sociaux, formulaire avec motif de demande

## Back-office (`/admin`)

- Tableau de bord (vue d'ensemble)
- Réservations (programmes / rendez-vous) — suivi de statut
- Inscriptions formation — suivi de statut
- Messages de contact
- Gestion des activités, produits, fournisseurs, clients

## Ce qu'il reste à faire

1. **Contenu réel** : remplacer les descriptions/images placeholder de chaque
   activité (modifiable directement depuis l'admin > Activités), compléter
   la page Contact (adresse, téléphone réels).
2. **Réseaux sociaux** : les liens Facebook/Instagram/TikTok sont des
   placeholders (`#`) dans `app/templates/base.html` et `contact.html` —
   à remplacer par les vrais liens du client.
3. **Réponse aux demandes** : actuellement, les réservations/inscriptions/
   messages sont juste enregistrés en base pour suivi dans l'admin. Si tu
   veux une notification automatique (email ou SMS envoyé au gérant dès
   qu'une demande arrive), on peut l'ajouter — dis-le moi.
4. **Déploiement** : base PostgreSQL sur Render (ou équivalent) + variables
   d'environnement en production.
5. **Design** : gabarit Bootstrap avec une couleur bordeaux par défaut
   (`#7a2447`) — à ajuster selon la charte graphique réelle du client (logo,
   couleurs, polices).

## Notes techniques

- Pas de paiement en ligne pour l'instant : chaque formulaire (réservation,
  formation, contact) crée juste une demande visible dans l'admin, à traiter
  par téléphone/email. Le module Kkiapay peut être réintégré plus tard si
  le besoin de paiement en ligne se confirme.
- Chaque formulaire de téléphone inclut un sélecteur d'indicatif pays
  (Bénin, Côte d'Ivoire, Togo, Ghana, Nigeria, Sénégal, etc. — liste dans
  `app/routes/public.py`, facile à étendre).
- Un même client (identifié par email) qui fait plusieurs demandes est
  reconnu et rattaché au même profil dans l'admin.
