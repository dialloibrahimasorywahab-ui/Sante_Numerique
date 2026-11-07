# Procédures de Sauvegarde et Restauration — Santé Numérique

Ce document spécifie la stratégie de sauvegarde, la rétention et les procédures opérationnelles de reprise après sinistre pour les données de santé de l'application **Santé Numérique**.

---

## 1. Stratégie de Sauvegarde

* **Fréquence** : Quotidienne (exécutée chaque nuit à 02h00 via cron).
* **Format** : `pg_dump -Fc` (PostgreSQL Custom Format compressé, garantissant l'intégrité transactionnelle et la portabilité).
* **Emplacement local** : Dossier `./backups/` sur l'hôte (exclu de Git).
* **Politique de rétention** : 30 jours glissants (les archives antérieures à 30 jours sont automatiquement purgées par le script).
* **Chiffrement** : Prise en charge native du chiffrement symétrique AES-256-CBC avec OpenSSL.

---

## 2. Automatisation Quotidienne (Cron)

Pour automatiser la sauvegarde chaque nuit sur le serveur de production, ajoutez une tâche planifiée dans la crontab de l'utilisateur exécutant Docker :

```bash
crontab -e
```

Ajoutez la ligne suivante :

```text
# Sauvegarde quotidienne de la base Santé Numérique à 02h00 du matin
0 2 * * * cd /opt/sante-numerique && bash scripts/backup.sh >> /var/log/sante_backup.log 2>&1
```

---

## 3. Exécution Manuelle d'une Sauvegarde

Pour déclencher immédiatement une sauvegarde (ex: avant une mise à jour applicative) :

```bash
bash scripts/backup.sh
```

### Chiffrement des archives de sauvegarde (Recommandé en Santé)

Pour chiffrer l'archive avec une clé secrète :

```bash
export BACKUP_ENCRYPTION_KEY="votre_cle_secrete_ultra_robuste"
bash scripts/backup.sh
```

Le script produit alors un fichier chiffré `.dump.enc` et supprime la version non chiffrée.

---

## 4. Procédure de Restauration d'Urgence

> [!WARNING]
> La restauration d'une base de données écrase l'état actif. Une sauvegarde de précaution automatique de l'état présent est toujours créée par le script avant toute manipulation.

### Syntaxe de la commande de restauration

```bash
bash scripts/restore.sh ./backups/sante_db_YYYYMMDD_HHMMSS.dump
```

Si le fichier est chiffré :

```bash
export BACKUP_ENCRYPTION_KEY="votre_cle_secrete_ultra_robuste"
bash scripts/restore.sh ./backups/sante_db_YYYYMMDD_HHMMSS.dump.enc
```

### Étapes exécutées par le script de restauration

1. Déchiffrement temporaire de l'archive si nécessaire.
2. Demande de confirmation explicite avec saisie obligatoire de `OUI`.
3. Création automatique d'un dump de sécurité de l'état actuel (`pre_restore_safety_*.dump`).
4. Arrêt gracieux du conteneur Backend pour couper les connexions concurrentes.
5. Déconnexion forcée des sessions PostgreSQL résiduelles.
6. Restauration atomique du schéma et des tables via `pg_restore`.
7. Redémarrage du Backend et vérification de santé.

---

## 5. Test Périodique de Restauration (Obligation Réglementaire)

> [!IMPORTANT]
> Conformément aux règles de sécurité en milieu hospitalier, une sauvegarde n'est considérée comme valide que si elle a été restaurée et vérifiée au moins une fois par trimestre sur un environnement de test isolé.

### Procédure de test sur environnement isolé

```bash
# 1. Création d'une base temporaire de test
docker compose exec db psql -U sante_user -d postgres -c "CREATE DATABASE test_restore_audit;"

# 2. Restauration de l'archive dans la base de test
cat ./backups/derniere_sauvegarde.dump | docker compose exec -T db pg_restore -U sante_user -d test_restore_audit --no-owner

# 3. Vérification du décompte des lignes dans les tables clés
docker compose exec db psql -U sante_user -d test_restore_audit -c "SELECT count(*) FROM users_user;"
docker compose exec db psql -U sante_user -d test_restore_audit -c "SELECT count(*) FROM patients_patient;"
docker compose exec db psql -U sante_user -d test_restore_audit -c "SELECT count(*) FROM consultation_consultation;"

# 4. Suppression de la base de test après validation
docker compose exec db psql -U sante_user -d postgres -c "DROP DATABASE test_restore_audit;"
```

