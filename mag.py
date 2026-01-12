import streamlit as st
from datetime import datetime
from supabase import create_client, Client

# --- KONFIGURACJA SUPABASE ---
# Znajdziesz te dane w panelu Supabase: Project Settings -> API
SUPABASE_URL = "TWOJ_URL_SUPABASE"
SUPABASE_KEY = "TWOJ_KLUCZ_API_SUPABASE"

@st.cache_resource
def init_connection():
    """Inicjalizuje połączenie z bazą danych Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Próba połączenia
try:
    supabase = init_connection()
except Exception as e:
    st.error(f"Nie udało się połączyć z bazą danych: {e}")

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
    """Pobiera wszystkie rekordy z bazy."""
    try:
        response = supabase.table("magazyn").select("*").execute()
        return response.data
    except Exception:
        return []

def dodaj_towar_db(nazwa, ilosc, kategoria):
    """Dodaje towar lub aktualizuje jego ilość."""
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().isoformat()
    
    # Sprawdzenie czy towar już jest w bazie
    existing = supabase.table("magazyn").select("*").eq("nazwa", nazwa).eq("kategoria", kategoria).execute()
    
    if existing.data:
        # Aktualizacja istniejącego
        nowa_ilosc = existing.data[0]['ilosc'] + ilosc
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc, 
            "ostatnia_aktualizacja": teraz
        }).eq("id", existing.data[0]['id']).execute()
    else:
        # Wstawienie zupełnie nowego towaru
        supabase.table("magazyn").insert({
            "nazwa": nazwa.strip(),
            "kategoria": kategoria,
            "ilosc": ilosc,
            "data_dodania": teraz,
            "ostatnia_aktualizacja": teraz
        }).execute()
    st.success(f"Dodano: {nazwa}")

def odejmij_ilosc_db(towar_obj, ilosc_do_odjecia):
    """Wydaje towar z bazy."""
    teraz = datetime.now().isoformat()
    
    if ilosc_do_odjecia > towar_obj['ilosc']:
        st.error(f"Nie ma tyle towaru! Dostępne: {towar_obj['ilosc']}")
        return False

    if ilosc_do_odjecia == towar_obj['ilosc']:
        # Usuwamy rekord jeśli stan wynosi 0
        supabase.table("magazyn").delete().eq("id", towar_obj['id']).execute()
        st.success(f"Wydano wszystko: {towar_obj['nazwa']}")
    else:
        # Zmniejszamy ilość
        nowa_ilosc = towar_obj['ilosc'] - ilosc_do_odjecia
        supabase.table("magazyn").update({
            "ilosc": nowa_ilosc,
            "ostatnia_aktualizacja": teraz
        }).eq("id", towar_obj['id']).execute()
        st.success(f"Wydano {ilosc_do_odjecia} szt. {towar_obj['nazwa']}")
    return True

# --- INTERFEJS UŻYTKOWNIKA ---

st.title("📦 System Magazynowy Supabase")

# Odświeżenie listy towarów
lista_towarow = pobierz_towary()

# 1. SEKACJA: DODAWANIE
st.header("➕ Dodaj Towar")
with st.form("dodawanie", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1:
        n_in = st.text_input("Nazwa")
        k_in = st.selectbox("Kategoria", KATEGORIE)
    with c2:
        i_in = st.number_input("Ilość", min_value=1, step=1)
    
    if st.form_submit_button("Dodaj do magazynu"):
        dodaj_towar_db(n_in, i_in, k_in)
        st.rerun()

# 2. SEKCJA: WYDAWANIE
st.header("➖ Wydaj Towar")
if lista_towarow:
    szukaj = st.text_input("🔍 Wyszukaj (wpisz nazwę)", key="szukaj_wydaj").lower()
    przefiltrowane = [t for t in lista_towarow if szukaj in t['nazwa'].lower()]

    if przefiltrowane:
        opcje = [f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" for t in przefiltrowane]
        wybor = st.selectbox("Wybierz towar z listy", options=opcje)
        
        idx = opcje.index(wybor)
        towar_do_wydania = przefiltrowane[idx]

        with st.form("wydawanie", clear_on_submit=True):
            ile_wy = st.number_input("Ile sztuk wydać?", min_value=1, step=1)
            if st.form_submit_button("Potwierdź wydanie"):
                if odejmij_ilosc_db(towar_do_wydania, ile_wy):
                    st.rerun()
    else:
        st.warning("Nie znaleziono towaru.")
else:
    st.info("Magazyn jest pusty.")

# 3. SEKCJA: TABELA STANÓW
st.header("📋 Aktualny Stan")
if lista_towarow:
    filtr_kat = st.selectbox("Filtruj wg kategorii:", ["Wszystko"] + KATEGORIE)
    
    dane_tabela = lista_towarow if filtr_kat == "Wszystko" else [t for t in lista_towarow if t['kategoria'] == filtr_kat]
    
    if dane_tabela:
        st.dataframe(
            dane_tabela,
            column_order=("nazwa", "kategoria", "ilosc", "data_dodania", "ostatnia_aktualizacja"),
            column_config={
                "nazwa": "Nazwa produktu",
                "kategoria": "Kategoria",
                "ilosc": "Stan",
                "data_dodania": "Data wpisu",
                "ostatnia_aktualizacja": "Ostatnia zmiana"
            },
            use_container_width=True,
            hide_index=True
        )
        st.write(f"**Łączna ilość sztuk:** {sum(t['ilosc'] for t in dane_tabela)}")
else:
    st.info("Brak towarów do wyświetlenia.")

# --- STOPKA / ADMINISTRACJA ---
st.markdown("---")
if st.button("🔴 Usuń całą zawartość bazy"):
    if st.session_state.get('potwierdzenie'):
        supabase.table("magazyn").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        st.success("Baza została wyczyszczona.")
        st.session_state['potwierdzenie'] = False
        st.rerun()
    else:
        st.warning("Jesteś pewien? Kliknij ponownie, aby potwierdzić.")
        st.session_state['potwierdzenie'] = True
