import streamlit as st
import folium
from streamlit_folium import st_folium

st.title("Tournée de ramassage (fictive)")

# Exemple d'itinéraire fictif
route = [
    (48.858370, 2.294481),  # Tour Eiffel
    (48.860611, 2.337644),  # Louvre
    (48.853, 2.3499),       # Notre-Dame
    (48.887535, 2.320493),  # Maxime
    (-0.253762, 41.703106)  # Somalie
]

m = folium.Map(location=route[0], zoom_start=13)
folium.PolyLine(route, color="blue", weight=5, opacity=0.7).add_to(m)
for idx, point in enumerate(route):
    folium.Marker(point, tooltip=f"Étape {idx+1}").add_to(m)

st_folium(m, width=700, height=500)
