# gym_progress_web.py
import streamlit as st
import pandas as pd
import datetime as dt

CSV_PATH = "allenamenti.csv"
DATE_FMT = "%Y-%m-%d"

def load_data():
    try:
        df = pd.read_csv(CSV_PATH)
        df["data"] = pd.to_datetime(df["data"], errors="coerce")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["data", "esercizio", "peso_kg", "ripetizioni", "serie", "tempo_min", "ROM", "volume", "densita", "e1rm"])
    return df

def save_data(df):
    df_out = df.copy()
    df_out["data"] = df_out["data"].dt.strftime(DATE_FMT)
    df_out.to_csv(CSV_PATH, index=False)

def calc_metrics(peso, rip, serie, tempo, rom):
    volume = peso * rip * serie
    densita = volume / tempo if tempo > 0 else 0
    e1rm = peso * (1 + rip / 30)
    return volume, densita, e1rm

st.title("🏋️‍♂️ Gym Progress Coach (Web)")

# Form inserimento dati
with st.form("new_session"):
    data = st.date_input("Data", dt.date.today())
    esercizio = st.text_input("Esercizio", "Panca Piana")
    peso = st.number_input("Peso (kg)", 0.0, 500.0, 80.0, 0.5)
    rip = st.number_input("Ripetizioni", 1, 50, 8)
    serie = st.number_input("Serie", 1, 20, 4)
    tempo = st.number_input("Tempo allenamento (min)", 1.0, 300.0, 25.0, 0.5)
    rom = st.number_input("ROM (0–1)", 0.0, 1.2, 0.95, 0.01)
    submitted = st.form_submit_button("Salva sessione")

df = load_data()

if submitted:
    volume, densita, e1rm = calc_metrics(peso, rip, serie, tempo, rom)
    new_row = {
        "data": pd.to_datetime(data),
        "esercizio": esercizio,
        "peso_kg": peso,
        "ripetizioni": rip,
        "serie": serie,
        "tempo_min": tempo,
        "ROM": rom,
        "volume": volume,
        "densita": densita,
        "e1rm": e1rm
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    st.success("✅ Sessione salvata!")

# Mostra storico
st.subheader("📋 Storico allenamenti")
st.dataframe(df.sort_values("data"))

# Analisi progresso
st.subheader("📈 Analisi progresso")
esercizi = df["esercizio"].unique()
if len(esercizi) > 0:
    esercizio_sel = st.selectbox("Scegli esercizio", esercizi)
    dfe = df[df["esercizio"] == esercizio_sel].sort_values("data")

    if len(dfe) >= 2:
        last = dfe.iloc[-1]
        prev = dfe.iloc[-2]
        for metric in ["volume", "densita", "e1rm"]:
            delta = ((last[metric] - prev[metric]) / prev[metric]) * 100
            arrow = "↑" if delta > 0 else "↓"
            st.write(f"{metric.capitalize()}: {last[metric]:.2f} ({arrow} {delta:.1f}%)")
        rom_delta = ((last["ROM"] - prev["ROM"]) / prev["ROM"]) * 100
        arrow = "↑" if rom_delta > 0 else "↓"
        st.write(f"ROM: {last['ROM']:.2f} ({arrow} {rom_delta:.1f}%)")
    else:
        st.info("Poche sessioni per questo esercizio.")

    # Grafici
    st.line_chart(dfe.set_index("data")[["volume", "densita", "e1rm", "ROM"]])
else:
    st.info("Aggiungi almeno una sessione per iniziare l'analisi.")

