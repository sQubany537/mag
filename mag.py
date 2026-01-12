import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
# Znajdziesz te dane w: Project Settings -> API w panelu Supabase
SUPABASE_URL = "https://otwxznkrtjlwdbyigynd.supabase.co"
SUPABASE_KEY = "sb_publishable_N7vU6pwrB7EPLm9bFo-foA_kGHrhyMH"

@st.cache_resource
def init_connection():
    """Inicjalizuje połączenie z bazą danych Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Nie udało się połączyć z Supabase. Sprawdź URL i Klucz API. Błąd: {e}")

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="Magazyn Supabase",
    page_icon="📦",
    layout="centered"
)

# Lista dostępnych kategorii
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- FUNKCJE BAZY DANYCH ---

def pobierz_towary():
    """Pobiera wszystkie towary z tabeli 'magazyn'."""
    try:
        response = supabase.table("magazyn").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Błąd podczas pobierania danych: {e}")
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    """Dodaje nowy towar lub zwiększa ilość istniejącego w bazie."""
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    
    # Sprawdzenie czy towar o tej samej nazwie i kategorii już istnieje
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        # Aktualizacja istniejącego wpisu
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        #
