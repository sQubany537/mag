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

# --- Funkcje Magazynu ---

def dodaj_towar(nazwa, ilosc):
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość (musi być > 0).")
        return

    # Pobieramy aktualny czas i formatujemy go
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    znaleziono = False
    for towar in st.session_state['towary']:
        if towar['nazwa'].lower() == nazwa.lower():
            towar['ilosc'] += ilosc
            # Aktualizujemy datę przy dołożeniu towaru
            towar['ostatnia_aktualizacja'] = teraz
            znaleziono = True
            break
    
    if not znaleziono:
        st.session_state['towary'].append({
            'nazwa': nazwa.strip(),
            'ilosc': ilosc,
            'data_dodania': teraz,
            'ostatnia_aktualizacja': teraz
        })
    st.success(f"Dodano/Zaktualizowano towar: **{nazwa}**")

def odejmij_ilosc(nazwa, ilosc_do_odjecia):
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for i, towar in enumerate(st.session_state['towary']):
        if towar['nazwa'] == nazwa:
            if ilosc_do_odjecia >= towar['ilosc']:
                st.session_state['towary'].pop(i)
                st.success(f"Towar **{nazwa}** został usunięty.")
            else:
                towar['ilosc'] -= ilosc_do_odjecia
                towar['ostatnia_aktualizacja'] = teraz
                st.success(f"Zmniejszono ilość towaru **{nazwa}**.")
            return

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")

# 1. Dodawanie/Aktualizowanie Towaru
st.header("➕ Dodaj / Zaktualizuj Towar")
with st.form("form_dodaj"):
    nazwa_dodaj = st.text_input("Nazwa Towaru")
    ilosc_dodaj = st.number_input("Ilość do dodania", min_value=1, value=1)
    if st.form_submit_button("Dodaj do magazynu"):
        dodaj_towar(nazwa_dodaj, ilosc_dodaj)

# 2. Wydawanie Towaru
st.header("➖ Wydaj z Magazynu")
opcje_usun = [towar['nazwa'] for towar in st.session_state['towary']]

if opcje_usun:
    with st.form("form_usun"):
        wybrany_towar = st.selectbox("Wybierz towar", options=opcje_usun)
        aktualna_ilosc = next(t['ilosc'] for t in st.session_state['towary'] if t['nazwa'] == wybrany_towar)
        ilosc_usun = st.number_input(f"Ile sztuk odjąć? (Obecnie: {aktualna_ilosc})", 
                                     min_value=1, max_value=aktualna_ilosc, value=1)
        if st.form_submit_button("Potwierdź wydanie"):
            odejmij_ilosc(wybrany_towar, ilosc_usun)
            st.rerun()
else:
    st.info("Brak towarów.")

# 3. Wyświetlanie Stanu Magazynu
st.header("📋 Stan Magazynu")
if st.session_state['towary']:
    # Mapowanie nazw kolumn dla lepszej czytelności w tabeli
    st.dataframe(
        st.session_state['towary'], 
        column_config={
            "nazwa": "Nazwa Towaru",
            "ilosc": "Ilość",
            "data_dodania": "Data Pierwszego Dodania",
            "ostatnia_aktualizacja": "Ostatnia Zmiana"
        },
        use_container_width=True, 
        hide_index=True
    )
else:
    st.info("Magazyn jest pusty.")

# Administracja
if st.button("Wyczyść Cały Magazyn"):
    st.session_state['towary'] = []
    st.rerun()
