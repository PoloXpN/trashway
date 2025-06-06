import streamlit as st
import requests
import pandas as pd
import pandas as pd

st.title("Historique des mesures")
backend_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")

# Add a refresh button
if st.button("Rafraîchir les données"):
    st.session_state.refresh_history = True

try:
    r = requests.get(f"{backend_url}/bins/")
    if r.status_code == 200:
        data = r.json()
        if data:
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Display map of bin locations
            st.subheader("Localisation des poubelles")
            st.map(df[['latitude', 'longitude']])
            # Display summary information
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Nombre total de mesures", len(df))
            with col2:
                st.metric("Nombre de poubelles", len(df["bin_id"].unique()))
            with col3:
                st.metric("Poids total (kg)", round(df["weight"].sum(), 2))
            # Show the data (without address columns)
            st.subheader("Données brutes")
            st.dataframe(df)
            # Visualisations
            st.subheader("Visualisations")
            # Presence distribution
            presence_counts = df["presence"].value_counts()
            st.write("Répartition des statuts de présence")
            st.bar_chart(presence_counts)
        else:
            st.info("Aucune donnée disponible.")
    else:
        st.error(f"Erreur: {r.text}")
except Exception as e:
    st.error(f"Erreur de connexion: {e}")
