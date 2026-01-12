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

# Próba nawiązania połączenia
try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Błąd połączenia: {e}")

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
    except Exception:
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    """Dodaje nowy towar lub zwiększa ilość istniejącego."""
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    
    # Sprawdzenie czy towar już istnieje
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        # Aktualizacja ilości
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        # Wstawienie nowego towaru (poprawione wcięcia)
        supabase.table("magazyn").insert({
            "nazwa": nazwa.strip(),
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Zaktualizowano: {nazwa}")

def odejmij_ilosc_db(towar_id, aktualna_ilosc, ilosc_do_odjecia):
    """Zmniejsza ilość towaru lub usuwa go, jeśli wydano wszystko."""
    teraz = datetime.now().isoformat()
    
    if ilosc_do_odjecia > aktualna_ilosc:
        st.error(f"Nie ma takiej ilości! Dostępne: {aktualna_ilosc}")
        return False

    if ilosc_do_odjecia == aktualna_ilosc:
        supabase.table("magazyn").delete().eq("id", towar_id).execute()
        st.success("Towar usunięty (wydano wszystko).")
    else:
        nowa_ilosc = aktualna_ilosc - ilosc_do_odjecia
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc,
            "ostatnia_aktualizacja": teraz
        }).eq("id", towar_id).execute()
        st.success(f"Wydano {ilosc_do_odjecia} sztuk.")
    return True

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("📦 Magazyn z Bazą Supabase")

# Pobranie danych z bazy
lista_towarow = pobierz_towary()

# 1. Dodawanie Towaru
st.header("➕ Dodaj / Zaktualizuj Towar")
with st.form("form_dodaj", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nazwa_in = st.text_input("Nazwa Towaru")
        kat_in = st.selectbox("Kategoria", options=KATEGORIE)
    with col2:
        ilosc_in = st.number_input("Ilość", min_value=1, step=1)
    
    if st.form_submit_button("Wyślij do bazy"):
        dodaj_towar_db(nazwa_in, ilosc_in, kat_in)
        st.rerun()

# 2. Wydawanie Towaru
st.header("➖ Wydaj z Magazynu")
if lista_towarow:
    szukaj = st.text_input("🔍 Wyszukaj towar (nazwa)", key="search_wydaj").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]

    if przefiltrowane:
        opcje = [f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybrany_tekst = st.selectbox("Wybierz towar", options=opcje)
        
        idx = opcje.index(wybrany_tekst)
        wybrany_towar = przefiltrowane[idx]

        with st.form("form_wydaj", clear_on_submit=True):
            ile_wydac = st.number_input("Ile wydać?", min_value=1, step=1)
            if st.form_submit_button("Potwierdź wydanie"):
                if odejmij_ilosc_db(wybrany_towar['id'], wybrany_towar['ilosc'], ile_wydac):
                    st.rerun()
    else:
        st.warning("Nie znaleziono towaru.")
else:
    st.info("Baza danych jest pusta.")

# 3. Wyświetlanie Stanu
st.header("📋 Stan Magazynu")
if lista_towarow:
    wybrany_filtr = st.selectbox("Pokaż kategorię:", options=["Wszystko"] + KATEGORIE)
    
    dane_widok = lista_towarow if wybrany_filtr == "Wszystko" else [t for t in lista_towarow if t['kategoria'] == wybrany_filtr]
    
    if dane_widok:
        st.dataframe(
            dane_widok, 
            use_container_width=True, 
            hide_index=True,
            column_order=("nazwa", "kategoria", "ilosc", "data_dodania", "ostatnia_aktualizacja")
        )
        st.info(f"Suma sztuk w widoku: {sum(t['ilosc'] for t in dane_widok)}")
    else:
        st.write("Brak produktów w tej kategorii.")
else:
    st.info("Magazyn jest pusty.")

# --- ADMINISTRACJA ---
st.markdown("---")
if st.button("🔴 WYCZYŚĆ CAŁĄ BAZĘ"):
    if st.session_state.get('confirm_del', False):
        supabase.table("magazyn").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        st.success("Baza wyczyszczona.")
        st.session_state['confirm_del'] = False
        st.rerun()
    else:
        st.warning("Kliknij jeszcze raz, aby potwierdzić usunięcie wszystkiego!")
        st.session_state['confirm_del'] = True
