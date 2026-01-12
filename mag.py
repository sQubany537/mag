import streamlit as st
from datetime import datetime

# --- Konfiguracja Strony ---
st.set_page_config(
    page_title="Prosty Magazyn Towarów",
    page_icon="📦"
)

# --- Inicjalizacja Stanu Magazynu ---
if 'towary' not in st.session_state:
    st.session_state['towary'] = []

# Lista dostępnych kategorii
KATEGORIE = ["Żywność", "Materiały budowlane", "Mechanika", "Elektronika", "Odzież"]

# --- Funkcje Magazynu ---

def dodaj_towar(nazwa, ilosc, kategoria):
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość.")
        return

    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    znaleziono = False
    
    for towar in st.session_state['towary']:
        if towar['nazwa'].lower() == nazwa.lower() and towar['kategoria'] == kategoria:
            towar['ilosc'] += ilosc
            towar['ostatnia_aktualizacja'] = teraz
            znaleziono = True
            break
    
    if not znaleziono:
        st.session_state['towary'].append({
            'nazwa': nazwa.strip(),
            'kategoria': kategoria,
            'ilosc': ilosc,
            'data_dodania': teraz,
            'ostatnia_aktualizacja': teraz
        })
    st.success(f"Zaktualizowano stan: {nazwa}")

def odejmij_ilosc(towar_obj, ilosc_do_odjecia):
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if ilosc_do_odjecia >= towar_obj['ilosc']:
        nazwa_temp = towar_obj['nazwa']
        st.session_state['towary'].remove(towar_obj)
        st.success(f"Towar {nazwa_temp} został całkowicie wydany.")
    else:
        towar_obj['ilosc'] -= ilosc_do_odjecia
        towar_obj['ostatnia_aktualizacja'] = teraz
        st.success(f"Wydano {ilosc_do_odjecia} szt. Pozostało: {towar_obj['ilosc']}")

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")

# 1. Dodawanie Towaru
st.header("➕ Dodaj / Zaktualizuj Towar")
with st.form("form_dodaj", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nazwa_dodaj = st.text_input("Nazwa Towaru")
        kategoria_dodaj = st.selectbox("Kategoria", options=KATEGORIE)
    with col2:
        ilosc_dodaj = st.number_input("Ilość do dodania", min_value=1, step=1)
    
    if st.form_submit_button("Dodaj do magazynu"):
        dodaj_towar(nazwa_dodaj, ilosc_dodaj, kategoria_dodaj)
        st.rerun()

# 2. Wydawanie Towaru z Wyszukiwarką
st.header("➖ Wydaj z Magazynu")

if st.session_state['towary']:
    # --- SEKCA WYSZUKIWANIA ---
    search_query = st.text_input("🔍 Wyszukaj towar (wpisz nazwę)", key="search_input").lower()
    
    # Filtrowanie listy na podstawie wyszukiwania
    filtered_items = [
        t for t in st.session_state['towary'] 
        if search_query in t['nazwa'].lower() or search_query in t['kategoria'].lower()
    ]

    if filtered_items:
        # Tworzymy listę etykiet dla przefiltrowanych towarów
        opcje_wyswietlane = [
            f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" 
            for t in filtered_items
        ]
        
        wybrany_tekst = st.selectbox(
            "Wybierz towar z listy", 
            options=opcje_wyswietlane,
            key="wybor_towaru_wydaj"
        )
        
        # Pobieramy obiekt towaru na podstawie wybranego tekstu
        idx = opcje_wyswietlane.index(wybrany_tekst)
        towar_do_edycji = filtered_items[idx]
        max_do_wydania = towar_do_edycji['ilosc']

        with st.form("form_wydaj", clear_on_submit=True):
            ilosc_usun = st.number_input(
                f"Ile sztuk wydać? (Dostępne: {max_do_wydania})", 
                min_value=1, 
                max_value=max_do_wydania, 
                step=1
            )
            
            if st.form_submit_button("Potwierdź wydanie"):
                odejmij_ilosc(towar_do_edycji, ilosc_usun)
                st.rerun()
    else:
        st.warning("Nie znaleziono towaru pasującego do wyszukiwania.")
else:
    st.info("Brak towarów w magazynie.")

# 3. Wyświetlanie Stanu Magazynu
st.header("📋 Stan Magazynu")
if st.session_state['towary']:
    st.dataframe(
        st.session_state['towary'], 
        column_config={
            "nazwa": "Nazwa",
            "kategoria": "Kategoria",
            "ilosc": "Ilość",
            "data_dodania": "Data dodania",
            "ostatnia_aktualizacja": "Ostatnia zmiana"
        },
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("Magazyn jest pusty.")

# Administracja
st.markdown("---")
if st.button("Wyczyść Cały Magazyn"):
    st.session_state['towary'] = []
    st.rerun()
