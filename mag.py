import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
# Musisz pobrać te dane z panelu: Project Settings -> API
# URL powinien zaczynać się od https://
SUPABASE_URL = "otwxznkrtjlwdbyigynd" 
SUPABASE_KEY = "sb_publishable_N7vU6pwrB7EPLm9bFo-foA_kGHrhyMH"

# 1. INICJALIZACJA POŁĄCZENIA (TUTAJ BYŁ BŁĄD)
# Zmienna 'supabase' musi być stworzona tutaj, aby funkcje poniżej mogły jej używać
@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Tworzymy obiekt połączenia globalnie
try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Błąd konfiguracji połączenia: {e}")
    st.stop()

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn Supabase", page_icon="📦")
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- FUNKCJE BAZY DANYCH ---

def pobierz_towary():
    try:
        response = supabase.table("magazyn").select("*").execute()
        return response.data
    except Exception:
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    # Teraz 'supabase' jest już widoczny
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        supabase.table("magazyn").insert({
            "nazwa": nazwa.strip(),
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Dodano/Zaktualizowano: {nazwa}")

def odejmij_ilosc_db(towar_obj, ilosc_do_odjecia):
    teraz = datetime.now().isoformat()
    if ilosc_do_odjecia > towar_obj['ilosc']:
        st.error(f"Brak wystarczającej ilości! Dostępne: {towar_obj['ilosc']}")
        return False

    if ilosc_do_odjecia == towar_obj['ilosc']:
        supabase.table("magazyn").delete().eq("id", towar_obj['id']).execute()
    else:
        nowa_ilosc = towar_obj['ilosc'] - ilosc_do_odjecia
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc,
            "ostatnia_aktualizacja": teraz
        }).eq("id", towar_obj['id']).execute()
    return True

# --- INTERFEJS ---

st.title("📦 Magazyn Supabase")
lista_towarow = pobierz_towary()

# Dodawanie
st.header("➕ Dodaj Towar")
with st.form("dodaj", clear_on_submit=True):
    col1, col2 = st.columns(2)
    n_in = col1.text_input("Nazwa")
    k_in = col1.selectbox("Kategoria", KATEGORIE)
    i_in = col2.number_input("Ilość", min_value=1, step=1)
    if st.form_submit_button("Dodaj do bazy"):
        dodaj_towar_db(n_in, i_in, k_in)
        st.rerun()

# Wydawanie
st.header("➖ Wydaj z Magazynu")
if lista_towarow:
    szukaj = st.text_input("🔍 Szukaj towaru...").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]
    
    if przefiltrowane:
        opcje = [f"{t['nazwa']} | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybor = st.selectbox("Wybierz towar", options=opcje)
        wybrany_obj = przefiltrowane[opcje.index(wybor)]
        
        with st.form("wydaj", clear_on_submit=True):
            ile_wy = st.number_input("Ile wydać?", min_value=1, step=1)
            if st.form_submit_button("Potwierdź"):
                if odejmij_ilosc_db(wybrany_obj, ile_wy):
                    st.rerun()

# Tabela
st.header("📋 Stan Magazynu")
if lista_towarow:
    filtr = st.selectbox("Filtruj wg kategorii:", ["Wszystko"] + KATEGORIE)
    widok = lista_towarow if filtr == "Wszystko" else [t for t in lista_towarow if t['kategoria'] == filtr]
    st.dataframe(widok, use_container_width=True, hide_index=True)
