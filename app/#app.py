import lightgbm as lgb
import numpy as np
import pandas as pd
import plotly.express as px
import sqlite3
import streamlit as st

st.set_page_config(
    page_title='Octroi de Crédit - LightGBM', layout='wide'
)

# SEUIL FINANCIER OPTIMAL DÉFINI DANS LE NOTEBOOK
THRESHOLD = 0.18


# --- FONCTIONS BASE DE DONNÉES ET MODÈLE ---
@st.cache_resource
def load_model():
    # S'assurer d'avoir sauvegardé votre modèle LightGBM préalablement
    # ex: lgb_model.booster_.save_model('lightgbm_model.txt')
    return lgb.Booster(model_file='lightgbm_model.txt')


@st.cache_data
def get_client_ids():
    conn = sqlite3.connect('home_credit.db')
    ids = pd.read_sql_query('SELECT SK_ID_CURR FROM clients', conn)[
        'SK_ID_CURR'
    ].tolist()
    conn.close()
    return ids


def get_client_data(client_id):
    conn = sqlite3.connect('home_credit.db')
    df_client = pd.read_sql_query(
        f'SELECT * FROM clients WHERE SK_ID_CURR = {client_id}', conn
    )
    conn.close()
    return df_client


@st.cache_data
def get_global_stats():
    conn = sqlite3.connect('home_credit.db')
    df_global = pd.read_sql_query('SELECT * FROM clients LIMIT 5000', conn)
    conn.close()
    return df_global


# --- INTERFACE PRINCIPALE ---
st.title(' Dashboard d\'Evaluation de Crédit - LightGBM')

# 1. SELECTION CLIENT
client_ids = get_client_ids()
selected_id = st.selectbox('Sélectionner un Client (SK_ID_CURR) :', client_ids)

if st.button('Afficher / Charger les données'):
    st.session_state['current_client'] = get_client_data(selected_id)

if 'current_client' in st.session_state:
    df_client = st.session_state['current_client']

    st.subheader(f'Données du client : {selected_id}')

    # 2. ÉDITION / MODIFICATION DES CHAMPS
    st.write('###  Édition des données client')
    col1, col2, col3 = st.columns(3)

    edited_data = df_client.copy()

    # Exemple de champs modifiables clé pour la simulation d'octroi
    if 'AMT_INCOME_TOTAL' in edited_data.columns:
        edited_data['AMT_INCOME_TOTAL'] = col1.number_input(
            'Revenu Total (AMT_INCOME_TOTAL)',
            value=float(df_client['AMT_INCOME_TOTAL'].values[0]),
        )

    if 'AMT_CREDIT' in edited_data.columns:
        edited_data['AMT_CREDIT'] = col2.number_input(
            'Montant du Crédit (AMT_CREDIT)',
            value=float(df_client['AMT_CREDIT'].values[0]),
        )

    if 'AMT_ANNUITY' in edited_data.columns:
        edited_data['AMT_ANNUITY'] = col3.number_input(
            'Annuité (AMT_ANNUITY)',
            value=float(df_client['AMT_ANNUITY'].values[0]),
        )

    # 3. PRÉDICTION / BOUTON POUR LANCER LE MODÈLE
    st.markdown('---')
    if st.button('🚀 Lancer le modèle LightGBM'):
        model = load_model()

        # Préparation des features (exclusion de TARGET et SK_ID_CURR si présentes)
        features = [
            col
            for col in edited_data.columns
            if col not in ['TARGET', 'SK_ID_CURR']
        ]
        X_input = edited_data[features]

        # Calcul de la probabilité
        proba_default = model.predict(X_input)[0]

        st.subheader('Résultat de l\'évaluation :')

        # 4. AFFICHAGE ACCEPTÉ / REFUSÉ (VERT / ROUGE)
        if proba_default >= THRESHOLD:
            st.error(
                f'❌ **DEMANDE REFUSÉE** (Risque de défaut : {proba_default:.2%}'
                f' | Seuil max : {THRESHOLD:.2%})'
            )
            st.session_state['status'] = 'Refusé'
        else:
            st.success(
                f'✅ **DEMANDE ACCEPTÉE** (Risque de défaut : {proba_default:.2%}'
                f' | Seuil max : {THRESHOLD:.2%})'
            )
            st.session_state['status'] = 'Accepté'

        st.session_state['proba'] = proba_default

    # 5. GRAPHIQUES COMPARATIFS ET RECOMMANDATIONS
    st.markdown('---')
    st.subheader(' Positionnement du client & Explications')

    df_global = get_global_stats()

    feature_to_compare = st.selectbox(
        'Choisir un indicateur à comparer :',
        ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY'],
    )

    if feature_to_compare in edited_data.columns:
        val_client = edited_data[feature_to_compare].values[0]
        mean_global = df_global[feature_to_compare].mean()

        # Graphique de distribution
        fig = px.histogram(
            df_global,
            x=feature_to_compare,
            nbins=50,
            title=f'Distribution de {feature_to_compare} au sein de la population',
        )
        fig.add_vline(
            x=val_client,
            line_dash='dash',
            line_color='red',
            annotation_text='Client actuel',
        )
        fig.add_vline(
            x=mean_global,
            line_dash='dot',
            line_color='blue',
            annotation_text='Moyenne Globale',
        )

        st.plotly_chart(fig, use_container_width=True)

        # Module Explicatif / Recommandations
        if st.session_state.get('status') == 'Refusé':
            st.warning('💡 **Conseils & Recommandations pour l\'octroi :**')
            st.write(
                f'- **Valeur actuelle de {feature_to_compare} :** {val_client:.2f}'
            )
            st.write(
                f'- **Moyenne du portefeuille :** {mean_global:.2f}'
            )

            if feature_to_compare == 'AMT_CREDIT' and val_client > mean_global:
                st.write(
                    '👉 *Recommandation :* Le montant demandé est supérieur'
                    ' à la moyenne. Réduire le montant du crédit pour repasser'
                    ' sous le seuil de risque.'
                )
            elif (
                feature_to_compare == 'AMT_INCOME_TOTAL'
                and val_client < mean_global
            ):
                st.write(
                    '👉 *Recommandation :* Une hausse future des revenus ou un'
                    ' co-emprunteur permettrait de sécuriser l\'octroi du'
                    ' prêt.'
                )