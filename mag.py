import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
SUPABASE_URL = "https://otwxznkrtjlwdbyigynd.supabase.co"
SUPABASE_KEY = "sb_publishable_N7vU6pwrB7EPLm9bFo-foA_kGHrhyMH"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"Błąd połączenia: {e}")
    st.stop()

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn Towarów", page_icon="📦")
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- FUNKCJE BAZY DANYCH (WSZYSTKO NA TABELI 'towary') ---

def pobierz_towary():
    try:
        # Zmieniono na "towary"
        response = supabase.table("towary").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Błąd pobierania: {e}")
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    # Zmieniono na "towary"
    existing = supabase.table("towary").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("towary").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        supabase.table("towary").insert({
            "nazwa": nazwa.strip(),
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Zaktualizowano: {nazwa}")

def odejmij_ilosc_db(towar_obj, ilosc_do_odjecia):
    teraz = datetime.now().isoformat()
    if ilosc_do_odjecia > towar_obj['ilosc']:
        st.error(f"Brak towaru! Dostępne: {towar_obj['ilosc']}")
        return False

    if ilosc_do_odjecia == towar_obj['ilosc']:
        # Zmieniono na "towary"
        supabase.table("towary").delete().eq("id", towar_obj['id']).execute()
    else:
        nowa_ilosc = towar_obj['ilosc'] - ilosc_do_odjecia
        supabase.table("towary").update({
            "ilosc": nowa_ilosc,
            "ostatnia_aktualizacja": teraz
        }).eq("id", towar_obj['id']).execute()
    return True

# --- INTERFEJS ---

st.title("📦 System: Towary")
lista_towarow = pobierz_towary()

# Sekcja Dodawania
st.header("➕ Dodaj towar")
with st.form("form_dodaj", clear_on_submit=True):
    c1, c2 = st.columns(2)
    n_in = c1.text_input("Nazwa")
    k_in = c1.selectbox("Kategoria", options=KATEGORIE)
    i_in = c2.number_input("Ilość", min_value=1, step=1)
    if st.form_submit_button("Dodaj"):
        dodaj_towar_db(n_in, i_in, k_in)
        st.rerun()

# Sekcja Wydawania
st.header("➖ Wydaj towar")
if lista_towarow:
    szukaj = st.text_input("🔍 Szukaj...", key="szukaj").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]
    
    if przefiltrowane:
        opcje = [f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybor = st.selectbox("Wybierz z listy", options=opcje)
        wybrany_obj = przefiltrowane[opcje.index(wybor)]
        
        with st.form("form_wydaj", clear_on_submit=True):
            ile_wy = st.number_input("Ile wydać?", min_value=1, max_value=wybrany_obj['ilosc'], step=1)
            if st.form_submit_button("Wydaj"):
                if odejmij_ilosc_db(wybrany_obj, ile_wy):
                    st.rerun()

# Tabela Stanów
st.header("📋 Aktualny stan")
if lista_towarow:
    st.dataframe(lista_towarow, use_container_width=True, hide_index=True, 
                 column_order=("nazwa", "kategoria", "ilosc", "ostatnia_aktualizacja"))
else:
    st.info("Baza 'towary' jest pusta.")

# Czyszczenie
if st.button("🔴 WYCZYŚĆ WSZYSTKO"):
    supabase.table("towary").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    st.rerun()
