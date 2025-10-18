import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# File per salvare i dati
DATA_FILE = 'budget_data.csv'

# Carica dati esistenti o crea un nuovo DataFrame
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=['Tipo', 'Categoria', 'Importo', 'Data'])

# Converti la colonna 'Data' in stringa per evitare problemi
df['Data'] = df['Data'].astype(str)

# Interfaccia principale
st.title("App per Monitorare Spese e Risparmi")

# Sidebar per inserimenti
st.sidebar.header("Aggiungi Transazione")
tipo = st.sidebar.selectbox("Tipo", ["Entrata", "Spesa"])
categoria = st.sidebar.text_input("Categoria (es. Stipendio, Cibo, Affitto)")
importo = st.sidebar.number_input("Importo (€)", min_value=0.0)
data = st.sidebar.date_input("Data", datetime.today())

if st.sidebar.button("Aggiungi"):
    # Converti la data in stringa
    new_row = pd.DataFrame({
        'Tipo': [tipo],
        'Categoria': [categoria],
        'Importo': [importo],
        'Data': [data.strftime('%Y-%m-%d')]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.sidebar.success("Transazione aggiunta!")

# Visualizzazione dati
st.header("Elenco Transazioni")
st.dataframe(df)

# Calcoli
st.header("Bilancio Mensile")
# Crea una lista di mesi disponibili o usa il mese corrente come default
if not df.empty:
    mesi = df['Data'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m')).unique()
else:
    mesi = [datetime.today().strftime('%Y-%m')]

mese = st.selectbox("Seleziona Mese", mesi)

# Filtra i dati per il mese selezionato
if not df.empty:
    df_mese = df[df['Data'].str.startswith(mese)]
else:
    df_mese = pd.DataFrame(columns=['Tipo', 'Categoria', 'Importo', 'Data'])

entrate = df_mese[df_mese['Tipo'] == 'Entrata']['Importo'].sum()
spese = df_mese[df_mese['Tipo'] == 'Spesa'].groupby('Categoria')['Importo'].sum()
risparmio_netto = entrate - spese.sum()

st.write(f"Entrate: €{entrate:.2f}")
st.write(f"Spese: €{spese.sum():.2f}")
st.write(f"Risparmio Netto: €{risparmio_netto:.2f}")

# Suggerimento per investimenti (es. regola 50/30/20)
st.header("Quanto Risparmiare per Investimenti")
percentuale_invest = st.slider("Percentuale da destinare a investimenti (%)", 10, 50, 20)
importo_invest = risparmio_netto * (percentuale_invest / 100)
st.write(f"Con il {percentuale_invest}% del risparmio netto, puoi investire: €{importo_invest:.2f}")

# Grafico spese per categoria
st.header("Grafico Spese per Categoria")
if not spese.empty:
    fig, ax = plt.subplots()
    # Aggiungi il grafico a torta con percentuali e legenda, senza etichette
    spese.plot(kind='pie', ax=ax, autopct='%1.1f%%', labels=None, legend=True)
    # Personalizza la legenda
    ax.legend(spese.index, title="Categorie", loc="center left", bbox_to_anchor=(1, 0.5))
    # Rimuovi l'etichetta y-axis per chiarezza
    ax.set_ylabel('')
    st.pyplot(fig)
else:
    st.write("Nessuna spesa registrata per questo mese.")

# Grafico andamento risparmio totale
st.header("Andamento Risparmio Totale")
if not df.empty:
    # Calcola il risparmio netto per ogni mese
    df['Mese'] = df['Data'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m'))
    risparmio_mensile = df.groupby(['Mese', 'Tipo'])['Importo'].sum().unstack(fill_value=0)
    risparmio_mensile['Risparmio'] = risparmio_mensile.get('Entrata', 0) - risparmio_mensile.get('Spesa', 0)
    
    # Crea il grafico a linee
    fig, ax = plt.subplots()
    risparmio_mensile['Risparmio'].plot(kind='line', ax=ax, marker='o')
    ax.set_xlabel('Mese')
    ax.set_ylabel('Risparmio Netto (€)')
    ax.set_title('Andamento del Risparmio Totale')
    ax.grid(True)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.write("Nessun dato disponibile per il grafico del risparmio.")