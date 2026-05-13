import streamlit as st
import datetime
import json
import os
from supabase import create_client, Client

# ==============================================================================
# 🎨 DESIGN E ESTILO
# ==============================================================================
st.set_page_config(page_title="ECO DECOR - Demanda diária", page_icon="📋", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    h1, h2, h3, h4 { color: #fafafa !important; }
    div.stButton > button {
        width: 100%; height: 50px; background-color: #5d7cf3 !important;
        color: white !important; font-weight: bold !important
