import streamlit as st
import requests
import datetime
import pandas as pd

st.title("Gestion des poubelles")

# Create tabs for different functionalities
tab1, tab2 = st.tabs(["Enregistrer une poubelle", "Gérer les poubelles existantes"])

# Backend URL
backend_url = st.secrets.get("BACKEND_URL", "http://localhost:8000")

# Tab 1: Register a new bin
with tab1:
    st.header("Enregistrer une nouvelle poubelle")
    
    bin_id = st.text_input("ID de la poubelle", "bin-001", key="reg_bin_id")
    weight = st.number_input("Poids (kg)", min_value=0.0, max_value=100.0, value=10.0, key="reg_weight")
    presence = st.selectbox("Présence détectée", [0, 1], key="reg_presence")
    timestamp = st.text_input("Timestamp (optionnel)", value=datetime.datetime.utcnow().isoformat(), key="reg_timestamp")

    # Address fields
    st.subheader("Adresse")
    col1, col2 = st.columns(2)
    with col1:
        street_number = st.text_input("Numéro de rue", "1", key="reg_street_number")
        postal_code = st.text_input("Code postal", "75000", key="reg_postal_code")
        country = st.text_input("Pays", "France", key="reg_country")
    with col2:
        street_name = st.text_input("Nom de rue", "Rue de Paris", key="reg_street_name")
        city = st.text_input("Ville", "Paris", key="reg_city")

    if st.button("Enregistrer"):
        data = {
            "bin_id": bin_id,
            "weight": weight,
            "presence": presence,
            "timestamp": timestamp,
            "street_number": street_number,
            "street_name": street_name,
            "postal_code": postal_code,
            "city": city,
            "country": country
        }
        try:
            r = requests.post(f"{backend_url}/bins/", json=data)
            if r.status_code == 200:
                st.success(f"Enregistré ! ID: {r.json().get('id')}")
            else:
                st.error(f"Erreur: {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion: {e}")

# Tab 2: Manage existing bins
with tab2:
    st.header("Gérer les poubelles existantes")
    
    # Initialize session state for managing delete confirmation
    if 'delete_confirmation_open' not in st.session_state:
        st.session_state.delete_confirmation_open = False
    if 'bin_to_delete' not in st.session_state:
        st.session_state.bin_to_delete = None
    
    # Add a refresh button
    if st.button("Rafraîchir les données"):
        st.session_state.refresh_bins = True
    
    # Fetch bins data
    try:
        r = requests.get(f"{backend_url}/bins/")
        if r.status_code == 200:
            bins_data = r.json()
            if bins_data:
                df = pd.DataFrame(bins_data)
                
                # Display the data in a table
                st.dataframe(df)
                
                # Select bin to manage
                bin_ids = [f"{bin['id']} - {bin['bin_id']}" for bin in bins_data]
                selected_bin = st.selectbox("Sélectionner une poubelle à gérer", bin_ids)
                if selected_bin:
                    bin_id = int(selected_bin.split(" - ")[0])
                    selected_bin_data = next((bin for bin in bins_data if bin["id"] == bin_id), None)
                    
                    if selected_bin_data:
                        st.subheader(f"Poubelle: {selected_bin_data['bin_id']}")
                        
                        col1, col2 = st.columns(2)
                        
                        # Update presence status
                        with col1:
                            statut_presence = "Sur socle" if selected_bin_data['presence'] == 1 else "Hors socle"
                            st.write(f"Statut Présence : {statut_presence}")
                            presence_options = ["Hors socle", "Sur socle"]
                            new_presence_label = st.radio("Changer le statut", presence_options, index=selected_bin_data['presence'])
                            new_presence = presence_options.index(new_presence_label)  # 0 ou 1

                            if st.button("Mettre à jour la présence"):
                                try:
                                    r = requests.patch(f"{backend_url}/bins/{bin_id}/presence", 
                                                     json={"presence": new_presence})
                                    if r.status_code == 200:
                                        st.success("Présence mise à jour !")
                                        st.rerun()
                                    else:
                                        st.error(f"Erreur: {r.text}")
                                except Exception as e:
                                    st.error(f"Erreur de connexion: {e}")
                        
                        # Delete bin
                        with col2:
                            st.write("Supprimer cette poubelle")
                            if st.button("Supprimer"):
                                # Store the bin to delete and open confirmation dialog
                                st.session_state.bin_to_delete = bin_id
                                st.session_state.delete_confirmation_open = True
                    
                    # Handle delete confirmation dialog
                    if st.session_state.delete_confirmation_open:
                        with st.container():
                            st.warning("⚠️ Confirmation de suppression")
                            st.write("Êtes-vous sûr de vouloir supprimer cette poubelle ?")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Oui, supprimer"):
                                    try:
                                        r = requests.delete(f"{backend_url}/bins/{st.session_state.bin_to_delete}")
                                        if r.status_code == 200:
                                            st.success("Poubelle supprimée !")
                                            st.session_state.delete_confirmation_open = False
                                            st.session_state.bin_to_delete = None
                                            st.rerun()
                                        else:
                                            st.error(f"Erreur: {r.text}")
                                    except Exception as e:
                                        st.error(f"Erreur de connexion: {e}")
                            
                            with col2:
                                if st.button("Annuler"):
                                    st.session_state.delete_confirmation_open = False
                                    st.session_state.bin_to_delete = None
                                    st.rerun()
            else:
                st.info("Aucune poubelle enregistrée.")
        else:
            st.error(f"Erreur: {r.text}")
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
