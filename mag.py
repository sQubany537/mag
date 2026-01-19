import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
# Znajdziesz te dane w: Project Settings -> API w panelu Supabase
SUPABASE_URL = "otwxznkrtjlwdbyigynd"
SUPABASE_KEY = "sb_publishable_N7vU6pwrB7EPLm9bFo-foA_kGHrhyMH"

@st.cache_resource
def init_connection():
    """Inicjalizuje połączenie z bazą danych Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Próba połączenia
try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Błąd połączenia z bazą: {e}")

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Magazyn Supabase", page_icon="📦")

# Lista dostępnych kategorii
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- FUNKCJE BAZY DANYCH ---

def pobierz_towary():
    """Pobiera dane z Supabase."""
    try:
        response = supabase.table("magazyn").select("*").execute()
        return response.data
    except Exception:
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    """Dodaje lub aktualizuje towar."""
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    # Szukamy czy taki towar już istnieje
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        # Prawidłowe wcięcie po else
        supabase.table("magazyn").insert({
            "nazwa": nazwa.strip(),
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Zaktualizowano: {nazwa}")

def odejmij_ilosc_db(towar_obj, ilosc_do_odjecia):
    """Wydaje towar z bazy z kontrolą ilości."""
    teraz = datetime.now().isoformat()
    
    # Zabezpieczenie przed wydaniem większej ilości niż dostępna
    if ilosc_do_odjecia > towar_obj['ilosc']:
        st.error(f"Błąd: Nie ma takiej ilości! Dostępne tylko: {towar_obj['ilosc']}")
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

# --- INTERFEJS ---

st.title("📦 System Magazynowy Supabase")
lista_towarow = pobierz_towary()

# 1. Dodawanie
st.header("➕ Dodaj Towar")
with st.form("form_dodaj", clear_on_submit=True):
    c1, c2 = st.columns(2)
    n_in = c1.text_input("Nazwa")
    k_in = c1.selectbox("Kategoria", KATEGORIE)
    i_in = c2.number_input("Ilość", min_value=1, step=1)
    if st.form_submit_button("Dodaj do magazynu"):
        dodaj_towar_db(n_in, i_in, k_in)
        st.rerun()

# 2. Wydawanie
st.header("➖ Wydaj Towar")
if lista_towarow:
    szukaj = st.text_input("🔍 Wyszukaj towar...", key="szukaj_wydaj").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]

    if przefiltrowane:
        opcje = [f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybor = st.selectbox("Wybierz z listy", options=opcje)
        wybrany_obj = przefiltrowane[opcje.index(wybor)]

        with st.form("form_wydaj", clear_on_submit=True):
            ile_wy = st.number_input("Ile wydać?", min_value=1, step=1)
            if st.form_submit_button("Potwierdź wydanie"):
                if odejmij_ilosc_db(wybrany_obj, ile_wy):
                    st.rerun()
    else:
        st.warning("Nie znaleziono towaru.")
else:
    st.info("Magazyn jest pusty.")

# 3. Tabela
st.header("📋 Stan Magazynu")
if lista_towarow:
    filtr = st.selectbox("Filtruj kategorię:", ["Wszystko"] + KATEGORIE)
    widok = lista_towarow if filtr == "Wszystko" else [t for t in lista_towarow if t['kategoria'] == filtr]
    
    if widok:
        st.dataframe(widok, use_container_width=True, hide_index=True, 
                     column_order=("nazwa", "kategoria", "ilosc", "ostatnia_aktualizacja"))
        st.write(f"**Suma sztuk:** {sum(t['ilosc'] for t in widok)}")
    else:
        st.write("Brak produktów w tej kategorii.")

# --- ADMIN ---
st.markdown("---")
if st.button("🔴 WYCZYŚĆ MAGAZYN"):
    if st.session_state.get('potwierdz'):
        supabase.table("magazyn").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        st.session_state['potwierdz'] = False
        st.rerun()
    else:
        st.warning("Kliknij drugi raz, aby potwierdzić usunięcie wszystkiego!")
        st.session_state['potwierdz'] = True
