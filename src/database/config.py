import streamlit as st
from supabase import create_client, Client
from src.database.local_db import LocalDBClient

def get_supabase_client():
    url = ""
    key = ""
    try:
        url = st.secrets.get("SUPABASE_URL", "").strip()
        key = st.secrets.get("SUPABASE_KEY", "").strip()
    except Exception:
        pass

    if url and key:
        try:
            client = create_client(url, key)
            # test connection
            client.table("teachers").select("username").limit(1).execute()
            print("Successfully connected to Supabase Cloud Database.")
            return client
        except Exception as e:
            print(f"Supabase connection failed ({e}). Falling back to local SQLite database.")
    else:
        print("No valid Supabase credentials found. Using local SQLite database.")
    return LocalDBClient()

supabase = get_supabase_client()