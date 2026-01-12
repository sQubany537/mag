import streamlit as st

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

    znaleziono = False
    for towar in st.session_state['towary']:
        if towar['nazwa'].lower() == nazwa.lower():
            towar['ilosc'] += ilosc
            znaleziono = True
            break
    
    if not znaleziono:
        st.session_state['towary'].append({
            'nazwa': nazwa.strip(),
            'ilosc': ilosc
        })
    st.success(f"Dodano/Zaktualizowano towar: **{nazwa}**")

def odejmij_ilosc(nazwa, ilosc_do_odjecia):
    """Zmniejsza ilość towaru lub usuwa go całkowicie, jeśli ilość spadnie do 0."""
    for i, towar in enumerate(st.session_state['towary']):
        if towar['nazwa'] == nazwa:
            if ilosc_do_odjecia >= towar['ilosc']:
                # Jeśli odejmujemy tyle samo lub więcej niż jest w magazynie - usuwamy wpis
                st.session_state['towary'].pop(i)
                st.success(f"Towar **{nazwa}** został całkowicie usunięty z magazynu.")
            else:
                # W przeciwnym razie tylko zmniejszamy licznik
                towar['ilosc'] -= ilosc_do_odjecia
                st.success(f"Zmniejszono ilość towaru **{nazwa}** o {ilosc_do_odjecia}. Pozostało: {towar['ilosc']}")
            return
    st.error("Nie znaleziono towaru.")

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")

# 1. Dodawanie/Aktualizowanie Towaru
st.header("➕ Dodaj / Zaktualizuj Towar")
with st.form("form_dodaj"):
    nazwa_dodaj = st.text_input("Nazwa Towaru")
    ilosc_dodaj = st.number_input("Ilość do dodania", min_value=1, value=1)
    if st.form_submit_button("Dodaj do magazynu"):
        dodaj_towar(nazwa_dodaj, ilosc_dodaj)

# 2. Usuwanie Częściowe lub Całkowite
st.header("➖ Wydaj z Magazynu (Odejmij)")
opcje_usun = [towar['nazwa'] for towar in st.session_state['towary']]

if opcje_usun:
    with st.form("form_usun"):
        wybrany_towar = st.selectbox("Wybierz towar", options=opcje_usun)
        
        # Znalezienie aktualnej ilości dla wybranego towaru, aby ustawić max_value w polu liczbowym
        aktualna_ilosc = next(t['ilosc'] for t in st.session_state['towary'] if t['nazwa'] == wybrany_towar)
        
        ilosc_usun = st.number_input(f"Ile sztuk odjąć? (Obecnie: {aktualna_ilosc})", 
                                     min_value=1, 
                                     max_value=aktualna_ilosc, 
                                     value=1)
        
        if st.form_submit_button("Potwierdź wydanie"):
            odejmij_ilosc(wybrany_towar, ilosc_usun)
            st.rerun() # Odświeżenie, aby zaktualizować listę i selectbox
else:
    st.info("Brak towarów do usunięcia.")

# 3. Wyświetlanie Stanu Magazynu
st.header("📋 Stan Magazynu")
if st.session_state['towary']:
    st.dataframe(st.session_state['towary'], use_container_width=True, hide_index=True)
    
    suma_towarow = sum(towar['ilosc'] for towar in st.session_state['towary'])
    st.markdown(f"**Łączna ilość sztuk w magazynie:** {suma_towarow}")
else:
    st.info("Magazyn jest pusty.")

# Opcje Administracyjne
st.subheader("⚠️ Opcje Administracyjne")
if st.button("Wyczyść Cały Magazyn"):
    st.session_state['towary'] = []
    st.rerun()
