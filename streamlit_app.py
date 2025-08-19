import streamlit as st
import pandas as pd
import datetime

# Inizializza storage (session_state)
if "workouts" not in st.session_state:
    st.session_state.workouts = []

# Funzione per aggiungere una sessione di allenamento
def add_workout(exercise, weight, reps, sets, duration):
    date = datetime.date.today()
    total_reps = reps * sets
    volume = weight * total_reps
    density = volume / duration if duration > 0 else 0
    avg_load = volume / total_reps if total_reps > 0 else 0

    st.session_state.workouts.append({
        "Data": str(date),
        "Esercizio": exercise,
        "Peso (kg)": weight,
        "Serie": sets,
        "Ripetizioni": reps,
        "Durata (min)": duration,
        "Volume": volume,
        "Densità": round(density, 2),
        "Carico medio per rep": round(avg_load, 2)
    })

# Funzione per calcolare feedback

def feedback(exercise):
    records = [w for w in st.session_state.workouts if w["Esercizio"] == exercise]
    if len(records) < 2:
        return "Non ci sono abbastanza dati per valutare la progressione."

    latest = records[-1]
    prev = records[-2]

    diff_volume = latest["Volume"] - prev["Volume"]
    diff_density = latest["Densità"] - prev["Densità"]

    fb = f"Progressione per {exercise} ({latest['Data']}):\n"
    fb += f"- Volume: {latest['Volume']} ({'+' if diff_volume>=0 else ''}{diff_volume})\n"
    fb += f"- Densità: {latest['Densità']} ({'+' if diff_density>=0 else ''}{diff_density:.2f})\n"

    if diff_volume > 0:
        fb += "Ottimo! Hai aumentato il volume."
    elif diff_volume < 0:
        fb += "Attenzione: volume in calo."

    return fb

# ===================== STREAMLIT APP =====================

st.title("🏋️ Tracciamento Progressi in Palestra")

st.subheader("Inserisci un nuovo allenamento")
with st.form("workout_form"):
    exercise = st.text_input("Esercizio", "Panca Piana")
    weight = st.number_input("Peso (kg)", min_value=0, value=60)
    reps = st.number_input("Ripetizioni", min_value=1, value=10)
    sets = st.number_input("Serie", min_value=1, value=3)
    duration = st.number_input("Durata (min)", min_value=1, value=30)
    submitted = st.form_submit_button("Aggiungi")

    if submitted:
        add_workout(exercise, weight, reps, sets, duration)
        st.success("Allenamento aggiunto!")

# Mostra storico allenamenti
if st.session_state.workouts:
    df = pd.DataFrame(st.session_state.workouts)
    st.subheader("📊 Storico Allenamenti")
    st.dataframe(df)

    # Selezione esercizio per feedback
    esercizi = df["Esercizio"].unique().tolist()
    scelta = st.selectbox("Seleziona esercizio per analisi:", esercizi)
    st.text(feedback(scelta))

    # Grafico progressione volume
    st.subheader("📈 Progressione Volume")
    chart_data = df[df["Esercizio"] == scelta][["Data", "Volume"]]
    st.line_chart(chart_data.set_index("Data"))


