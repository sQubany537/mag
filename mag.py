import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- Konfiguracja Supabase ---
# Wstaw tutaj swoje dane z panelu Supabase
SUPABASE_URL = "TWOJ_URL_SUPABASE"
SUPABASE_KEY = "TWOJ_KLUCZ_API_SUPABASE"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_connection()

# --- Konfiguracja Strony ---
st.set_page_config(
    page_title="Magazyn Supabase",
    page_icon="📦"
)

# Lista dostępnych kategorii
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- Funkcje Bazy Danych ---

def pobierz_towary():
    """Pobiera wszystkie towary z bazy Supabase."""
    response = supabase.table("magazyn").select("*").execute()
    return response.data

def dodaj_towar_db(nazwa, ilosc, kategoria):
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    
    # Sprawdź czy towar już istnieje
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        supabase.table("magazyn").insert({
            "nazwa": nazwa,
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Zaktualizowano: {nazwa}")

def odejmij_ilosc_db(towar_id, aktualna_ilosc, ilosc_do_odjecia):
    teraz = datetime.now().isoformat()
    
    if ilosc_do_odjecia > aktualna_ilosc:
        st.error(f"Błąd: Nie ma takiej ilości! Dostępne: {aktualna_ilosc}")
        return False

    if ilosc_do_odjecia == aktualna_ilosc:
        supabase.table("magazyn").delete().eq("id", towar_id).execute()
        st.success("Towar został całkowicie wydany i usunięty.")
    else:
        nowa_ilosc = aktualna_ilosc - ilosc_do_odjecia
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc,
            "ostatnia_aktualizacja": teraz
        }).eq("id", towar_id).execute()
        st.success(f"Wydano {ilosc_do_odjecia} szt.")
    return True

# --- Interfejs Użytkownika ---

st.title("📦 Magazyn z Bazą Supabase")

# Pobieranie aktualnych danych
lista_towarow = pobierz_towary()

# 1. Dodawanie Towaru
st.header("➕ Dodaj / Zaktualizuj")
with st.form("form_dodaj", clear_on_submit=True):
    c1, c2 = st.columns(2)
    nazwa_in = c1.text_input("Nazwa Towaru")
    kat_in = c1.selectbox("Kategoria", options=KATEGORIE)
    ilosc_in = c2.number_input("Ilość", min_value=1, step=1)
    if st.form_submit_button("Dodaj do bazy"):
        dodaj_towar_db(nazwa_in, ilosc_in, kat_in)
        st.rerun()

# 2. Wydawanie Towaru
st.header("➖ Wydaj z Magazynu")
if lista_towarow:
    szukaj = st.text_input("🔍 Szukaj towaru...", key="search").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]

    if przefiltrowane:
        opcje = [f"{t['nazwa']} ({t['kategoria']}) | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybrany_tekst = st.selectbox("Wybierz towar", options=opcje)
        
        idx = opcje.index(wybrany_tekst)
        wybrany_towar = przefiltrowane[idx]

        with st.form("form_wydaj", clear_on_submit=True):
            ile_wy dac = st.number_input("Ile wydać?", min_value=1, step=1)
            if st.form_submit_button("Potwierdź wydanie"):
                if odejmij_ilosc_db(wybrany_towar['id'], wybrany_towar['ilosc'], ile_wydac):
                    st.rerun()
else:
    st.info("Baza danych jest pusta.")

# 3. Wyświetlanie Stanu
st.header("📋 Stan Magazynu")
if lista_towarow:
    filtr_kat = st.selectbox("Pokaż kategorię:", ["Wszystko"] + KATEGORIE)
    widok = lista_towarow if filtr_kat == "Wszystko" else [t for t in lista_towarow if t['kategoria'] == filtr_kat]
    
    st.dataframe(widok, use_container_width=True, hide_index=True, column_order=("nazwa", "kategoria", "ilosc", "ostatnia_aktualizacja"))
    st.write(f"**Suma sztuk:** {sum(t['ilosc'] for t in widok)}")

# Administracja
if st.button("Wyczyść Cały Magazyn (TRWALE)"):
    supabase.table("magazyn").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    st.rerun()
