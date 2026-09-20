import sqlite3
import pandas as pd

conn = sqlite3.connect('credit_risk.db')
cursor = conn.cursor()

# 1. Lister toutes les tables présentes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('📋 Tables dans la BDD :', tables)

# 2. Vérifier le nombre de lignes dans client_features
try:
    count = cursor.execute(
        'SELECT COUNT(*) FROM client_features'
    ).fetchone()[0]
    print(f'🔢 Nombre de lignes dans client_features : {count}')

    # 3. Afficher les 5 premières colonnes et les 3 premières lignes
    df_sample = pd.read_sql_query('SELECT * FROM client_features LIMIT 3', conn)
    print(f'📐 Dimensions du DataFrame : {df_sample.shape}')
    print('\n🔹 Liste des 10 premières colonnes :')
    print(list(df_sample.columns[:10]))
    print('\n🔹 Aperçu des données :')
    print(df_sample.iloc[:, :5])

except Exception as e:
    print(f'❌ Erreur d\'accès à la table : {e}')

conn.close()