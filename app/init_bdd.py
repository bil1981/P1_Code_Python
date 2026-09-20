import sqlite3
import pandas as pd

# 1. Chargement des données d'entrée nettoyées
df = pd.read_parquet('./src/lightgbm_train_engineered.parquet')

# 2. Connexion à la base SQLite (crée le fichier s'il n'existe pas)
conn = sqlite3.connect('home_credit.db')

# 3. Export des données vers la table 'clients'
df.to_sql('clients', conn, if_exists='replace', index=False)

# Création d'un index sur SK_ID_CURR pour accélérer la recherche par client
cursor = conn.cursor()
cursor.execute(
    'CREATE INDEX IF NOT EXISTS idx_sk_id ON clients (SK_ID_CURR)'
)
conn.commit()
conn.close()

print('Base de données initialisée avec succès.')