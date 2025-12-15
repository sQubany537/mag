import streamlit as st

# --- Konfiguracja Strony ---
st.set_page_config(
    page_title="Prosty Magazyn Towarów",
    page_icon="📦"
)

# --- Inicjalizacja Stanu Magazynu ---
# Inicjalizuje listę towarów w st.session_state, jeśli jeszcze nie istnieje.
# Jest to kluczowe dla zachowania danych podczas interakcji użytkownika.
if 'towary' not in st.session_state:
    st.session_state['towary'] = []

# --- Funkcje Magazynu ---

def dodaj_towar(nazwa, ilosc):
    """Dodaje nowy towar do magazynu lub aktualizuje ilość istniejącego."""
    if not nazwa or ilosc <= 0:
        st.error("Wprowadź poprawną nazwę i ilość (musi być > 0).")
        return

    # Sprawdzenie, czy towar już istnieje
    znaleziono = False
    for towar in st.session_state['towary']:
        if towar['nazwa'].lower() == nazwa.lower():
            towar['ilosc'] += ilosc
            znaleziono = True
            break
    
    if not znaleziono:
        # Dodanie nowego towaru
        st.session_state['towary'].append({
            'nazwa': nazwa.strip(),
            'ilosc': ilosc
        })
    
    st.success(f"Dodano/Zaktualizowano towar: **{nazwa}**, Ilość: **{ilosc}**")

def usun_towar(nazwa):
    """Usuwa towar o podanej nazwie z magazynu."""
    # Używamy list comprehension do stworzenia nowej listy bez wskazanego towaru
    ilosc_przed = len(st.session_state['towary'])
    
    st.session_state['towary'] = [
        towar for towar in st.session_state['towary'] 
        if towar['nazwa'].lower() != nazwa.lower()
    ]
    
    ilosc_po = len(st.session_state['towary'])

    if ilosc_przed > ilosc_po:
        st.success(f"Usunięto towar: **{nazwa}**")
    else:
        st.warning(f"Nie znaleziono towaru o nazwie: **{nazwa}**")

# --- Interfejs Użytkownika Streamlit ---

st.title("📦 Prosty Magazyn Towarów")
st.markdown("Aplikacja do zarządzania stanem magazynowym za pomocą list w Streamlit.")

# 1. Dodawanie/Aktualizowanie Towaru
st.header("➕ Dodaj / Zaktualizuj Towar")

with st.form("form_dodaj"):
    nazwa_dodaj = st.text_input("Nazwa Towaru", key="input_nazwa_dodaj")
    ilosc_dodaj = st.number_input("Ilość do dodania", min_value=1, value=1, step=1, key="input_ilosc_dodaj")
    submitted_dodaj = st.form_submit_button("Dodaj Towar")
    
    if submitted_dodaj:
        dodaj_towar(nazwa_dodaj, ilosc_dodaj)

# 2. Usuwanie Towaru
st.header("➖ Usuń Towar")

# Tworzenie listy opcji do usunięcia na podstawie aktualnego stanu magazynu
opcje_usun = [towar['nazwa'] for towar in st.session_state['towary']]
nazwa_usun = st.selectbox("Wybierz towar do usunięcia", options=[""] + opcje_usun, key="select_nazwa_usun")

if st.button("Usuń Wybrany Towar") and nazwa_usun:
    usun_towar(nazwa_usun)

# 3. Wyświetlanie Stanu Magazynu
st.header("📋 Stan Magazynu")

if st.session_state['towary']:
    # Używamy st.dataframe do ładnego wyświetlenia listy towarów
    df_magazyn = st.dataframe(
        st.session_state['towary'], 
        use_container_width=True,
        hide_index=True,
        column_order=("nazwa", "ilosc") # Zapewnia kolejność kolumn
    )
    
    # Podsumowanie
    suma_towarow = sum(towar['ilosc'] for towar in st.session_state['towary'])
    liczba_unikalnych = len(st.session_state['towary'])
    
    st.markdown(f"**Podsumowanie:** Liczba unikalnych towarów: **{liczba_unikalnych}**, Łączna ilość sztuk: **{suma_towarow}**")

else:
    st.info("Magazyn jest pusty. Dodaj pierwszy towar!")

# Opcjonalny przycisk do wyczyszczenia wszystkiego
st.subheader("⚠️ Opcje Administracyjne")
if st.button("Wyczyść Cały Magazyn", help="Spowoduje trwałe usunięcie wszystkich danych z bieżącej sesji"):
    st.session_state['towary'] = []
    st.experimental_rerun() # Odświeżenie aplikacji po wyczyszczeniu
