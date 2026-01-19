import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
# Znajdziesz te dane w panelu Supabase: Project Settings -> API
# Pamiętaj: URL musi zaczynać się od https://
SUPABASE_URL = "otwxznkrtjlwdbyigynd"
SUPABASE_KEY = "sb_publishable_N7vU6pwrB7EPLm9bFo-foA_kGHrhyMH"

# 1. Inicjalizacja połączenia
@st.cache_resource
def init_connection():
    if "https://" not in SUPABASE_URL:
        st.error("Błąd: Adres SUPABASE_URL musi zaczynać się od 'https://'")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Tworzymy obiekt globalny 'supabase', aby uniknąć NameError
try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"Błąd konfiguracji połączenia: {e}")
    st.stop()

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn Supabase", page_icon="📦")

# Lista dostępnych kategorii
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- FUNKCJE BAZY DANYCH ---

def pobierz_towary():
    """Pobiera wszystkie rekordy z bazy danych."""
    try:
        response = supabase.table("magazyn").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    """Dodaje nowy towar lub aktualizuje stan istniejącego."""
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    
    # Sprawdzanie czy towar już istnieje
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        # Aktualizacja
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        # Wstawienie (poprawione wcięcia)
        supabase.table("magazyn").insert({
            "nazwa": nazwa.strip(),
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Zaktualizowano stan magazynu: {nazwa}")

def odejmij_ilosc_db(towar_obj, ilosc_do_odjecia):
    """Zmniejsza stan lub usuwa towar, jeśli wydano wszystko."""
    teraz = datetime.now().isoformat()
    
    if ilosc_do_odjecia > towar_obj['ilosc']:
        st.error(f"Błąd: Brak wystarczającej ilości! Dostępne: {towar_obj['ilosc']}")
        return False

    if ilosc_do_odjecia == towar_obj['ilosc']:
        supabase.table("magazyn").delete().eq("id", towar_obj['id']).execute()
        st.success(f"Wydano wszystko: {towar_obj['nazwa']}")
    else:
        nowa_ilosc = towar_obj['ilosc'] - ilosc_do_odjecia
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc,
            "ostatnia_aktualizacja": teraz
        }).eq("id", towar_obj['id']).execute()
        st.success(f"Wydano {ilosc_do_odjecia} szt. {towar_obj['nazwa']}")
    return True

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("📦 System Magazynowy Supabase")

# Pobieranie aktualnej listy
lista_towarow = pobierz_towary()

# 1. Dodawanie
st.header("➕ Dodaj / Zaktualizuj Towar")
with st.form("form_dodaj", clear_on_submit=True):
    col1, col2 = st.columns(2)
    n_in = col1.text_input("Nazwa Towaru")
    k_in = col1.selectbox("Kategoria", options=KATEGORIE)
    i_in = col2.number_input("Ilość do dodania", min_value=1, step=1)
    if st.form_submit_button("Wyślij do bazy"):
        dodaj_towar_db(n_in, i_in, k_in)
        st.rerun()

# 2. Wydawanie
st.header("➖ Wydaj z Magazynu")
if lista_towarow:
    szukaj = st.text_input("🔍 Wyszukaj towar do wydania", key="search").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]
    
    if przefiltrowane:
        opcje = [f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybor = st.selectbox("Wybierz towar z listy", options=opcje)
        wybrany_obj = przefiltrowane[opcje.index(wybor)]
        
        with st.form("form_wydaj", clear_on_submit=True):
            ile_wy = st.number_input("Ile sztuk wydać?", min_value=1, max_value=wybrany_obj['ilosc'], step=1)
            if st.form_submit_button("Potwierdź wydanie"):
                if odejmij_ilosc_db(wybrany_obj, ile_wy):
                    st.rerun()
    else:
        st.warning("Nie znaleziono takiego towaru.")
else:
    st.info("Baza danych jest pusta.")

# 3. Wyświetlanie tabeli
st.header("📋 Stan Magazynu")
if lista_towarow:
    filtr = st.selectbox("Pokaż kategorię:", ["Wszystko"] + KATEGORIE)
    widok = lista_towarow if filtr == "Wszystko" else [t for t in lista_towarow if t['kategoria'] == filtr]
    
    if widok:
        st.dataframe(
            widok, 
            column_order=("nazwa", "kategoria", "ilosc", "ostatnia_aktualizacja"),
            column_config={
                "nazwa": "Nazwa", "kategoria": "Kategoria", 
                "ilosc": "Ilość", "ostatnia_aktualizacja": "O
