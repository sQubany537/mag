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
        st.error("Wprowadź poprawną nazwę i ilość (musi być > 0).")
        return

    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Szukamy, czy towar o tej samej nazwie I kategorii już istnieje
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
    st.success(f"Dodano/Zaktualizowano towar: **{nazwa}** w kategorii **{kategoria}**")

def odejmij_ilosc(indeks, ilosc_do_odjecia):
    teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    towar = st.session_state['towary'][indeks]
    
    if ilosc_do_odjecia >= towar['ilosc']:
        st.session_state['towary'].pop(indeks)
        st.success(f"Towar **{towar['nazwa']}** został usunięty.")
    else:
        towar['ilosc'] -= ilosc_do_odjecia
        towar['ostatnia_aktualizacja'] = teraz
        st.success(f"Zmniejszono ilość towaru **{towar['nazwa']}**.")

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")

# 1. Dodawanie/Aktualizowanie Towaru
st.header("➕ Dodaj / Zaktualizuj Towar")
with st.form("form_dodaj"):
    col1, col2 = st.columns(2)
    with col1:
        nazwa_dodaj = st.text_input("Nazwa Towaru")
        kategoria_dodaj = st.selectbox("Kategoria", options=KATEGORIE)
    with col2:
        ilosc_dodaj = st.number_input("Ilość do dodania", min_value=1, value=1)
    
    if st.form_submit_button("Dodaj do magazynu"):
        dodaj_towar(nazwa_dodaj, ilosc_dodaj, kategoria_dodaj)

# 2. Wydawanie Towaru
st.header("➖ Wydaj z Magazynu")
if st.session_state['towary']:
    # Tworzymy listę opisową dla selectboxa, żeby odróżnić towary o tej samej nazwie w różnych kategoriach
    opcje_usun = [f"{t['nazwa']} ({t['kategoria']}) - dostępne: {t['ilosc']}" for t in st.session_state['towary']]
    
    with st.form("form_usun"):
        wybor_indeks = st.selectbox("Wybierz towar do wydania", options=range(len(opcje_usun)), format_func=lambda x: opcje_usun[x])
        ilosc_max = st.session_state['towary'][wybor_indeks]['ilosc']
        ilosc_usun = st.number_input(f"Ile sztuk odjąć?", min_value=1, max_value=ilosc_max, value=1)
        
        if st.form_submit_button("Potwierdź wydanie"):
            odejmij_ilosc(wybor_indeks, ilosc_usun)
            st.rerun()
else:
    st.info("Brak towarów w magazynie.")

# 3. Wyświetlanie Stanu Magazynu
st.header("📋 Stan Magazynu")
if st.session_state['towary']:
    # Opcja filtrowania po kategorii
    kat_filtr = st.multiselect("Filtruj wg kategorii:", options=KATEGORIE, default=KATEGORIE)
    
    widok_danych = [t for t in st.session_state['towary'] if t['kategoria'] in kat_filtr]
    
    st.dataframe(
        widok_danych, 
        column_config={
            "nazwa": "Nazwa Towaru",
            "kategoria": "Kategoria",
            "ilosc": "Ilość",
            "data_dodania": "Data Pierwszego Dodania",
            "ostatnia_aktualizacja": "Ostatnia Zmiana"
        },
        use_container_width=True, 
        hide_index=True
    )
    
    suma_sztuk = sum(t['ilosc'] for t in widok_danych)
    st.markdown(f"**Łączna ilość sztuk w wybranych kategoriach:** {suma_sztuk}")
else:
    st.info("Magazyn jest pusty.")

# Administracja
st.markdown("---")
if st.button("Wyczyść Cały Magazyn"):
    st.session_state['towary'] = []
    st.rerun()
