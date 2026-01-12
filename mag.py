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

def odejmij_ilosc(indeks, ilosc_do_odjecia):
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    towar = st.session_state['towary'][indeks]
    
    if ilosc_do_odjecia >= towar['ilosc']:
        nazwa_temp = towar['nazwa']
        st.session_state['towary'].pop(indeks)
        st.success(f"Towar {nazwa_temp} został całkowicie wydany i usunięty z listy.")
    else:
        towar['ilosc'] -= ilosc_do_odjecia
        towar['ostatnia_aktualizacja'] = teraz
        st.success(f"Wydano {ilosc_do_odjecia} szt. towaru {towar['nazwa']}. Pozostało: {towar['ilosc']}")

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

# 2. Wydawanie Towaru (Poprawiona sekcja)
st.header("➖ Wydaj z Magazynu")
if st.session_state['towary']:
    # Tworzymy listę opcji do wyboru
    opcje_wyswietlane = [
        f"{t['nazwa']} | {t['kategoria']} | Stan: {t['ilosc']}" 
        for t in st.session_state['towary']
    ]
    
    # Wybór towaru POZA formularzem, aby dynamicznie pobrać max_value
    wybrany_indeks = st.selectbox(
        "Wybierz towar do wydania", 
        options=range(len(opcje_wyswietlane)), 
        format_func=lambda x: opcje_wyswietlane[x],
        key="wybor_towaru_wydaj"
    )
    
    # Pobieramy aktualny towar na podstawie wyboru
    towar_do_edycji = st.session_state['towary'][wybrany_indeks]
    max_do_wydania = towar_do_edycji['ilosc']

    with st.form("form_wydaj", clear_on_submit=True):
        ilosc_usun = st.number_input(
            f"Ile sztuk wydać? (Maksymalnie: {max_do_wydania})", 
            min_value=1, 
            max_value=max_do_wydania, 
            step=1
        )
        
        if st.form_submit_button("Potwierdź wydanie"):
            odejmij_ilosc(wybrany_indeks, ilosc_usun)
            st.rerun()
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
