import streamlit as st
import pandas as pd
import datetime

# Inizializza storage (session_state)
if "workouts" not in st.session_state:
    st.session_state.workouts = []

# Funzione per aggiungere una sessione di allenamento
def add_workout(date, exercise, weight, reps_list, rest_time):
    total_reps = sum(reps_list)
    volume = weight * total_reps
    num_sets = len(reps_list)
    num_pauses = max(0, num_sets - 1)
    total_rest = rest_time * num_pauses
    density = volume / total_rest if total_rest > 0 else 0
    avg_load = volume / total_reps if total_reps > 0 else 0

    # Progress Score: media pesata di volume, densità e carico medio
    progress_score = (volume * 0.5) + (density * 0.3) + (avg_load * 0.2)

    st.session_state.workouts.append({
        "Data": str(date),
        "Esercizio": exercise,
        "Peso (kg)": weight,
        "Serie": num_sets,
        "Ripetizioni per serie": str(reps_list),
        "Ripetizioni totali": total_reps,
        "Recupero medio (s)": rest_time,
        "Volume": volume,
        "Densità": round(density, 2),
        "Carico medio per rep": round(avg_load, 2),
        "Progress Score": round(progress_score, 2)
    })

# Funzione per calcolare feedback globale
def feedback(exercise):
    records = [w for w in st.session_state.workouts if w["Esercizio"] == exercise]
    if len(records) < 2:
        return "Non ci sono abbastanza dati per valutare la progressione."

    latest = records[-1]
    prev = records[-2]

    diff_score = latest["Progress Score"] - prev["Progress Score"]

    fb = f"Progressione globale per {exercise} ({latest['Data']}):\n"
    fb += f"- Progress Score: {latest['Progress Score']} ({'+' if diff_score>=0 else ''}{round(diff_score,2)})\n"

    if diff_score > 0:
        fb += "📈 Ottimo! Sei in progresso complessivo."
    elif diff_score < 0:
        fb += "📉 Attenzione: regressione complessiva."
    else:
        fb += "➖ Nessun cambiamento rispetto alla scorsa sessione."

    return fb

# ===================== STREAMLIT APP =====================

st.title("🏋️ Tracciamento Progressi in Palestra")

st.subheader("Inserisci un nuovo allenamento")
with st.form("workout_form"):
    date = st.date_input("Data allenamento", datetime.date.today())
    exercise = st.text_input("Esercizio", "Panca Piana")
    weight = st.number_input("Peso (kg)", min_value=0, value=60)
    n_sets = st.number_input("Numero di serie", min_value=1, value=3)

    reps_list = []
    for i in range(int(n_sets)):
        r = st.number_input(f"Ripetizioni serie {i+1}", min_value=1, value=10, key=f"rep_{i}")
        reps_list.append(r)

    rest_time = st.number_input("Tempo medio di recupero tra le serie (secondi)", min_value=0, value=90)
    submitted = st.form_submit_button("Aggiungi")

    if submitted:
        add_workout(date, exercise, weight, reps_list, rest_time)
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

    # Grafico progressione densità
    st.subheader("⚡ Progressione Densità")
    chart_density = df[df["Esercizio"] == scelta][["Data", "Densità"]]
    st.line_chart(chart_density.set_index("Data"))

    # Grafico progressione score complessivo
    st.subheader("🌟 Progressione Globale (Progress Score)")
    chart_score = df[df["Esercizio"] == scelta][["Data", "Progress Score"]]
    st.line_chart(chart_score.set_index("Data"))

    # Sezione per eliminare allenamenti
    st.subheader("🗑️ Gestione Allenamenti")

    # Eliminare un singolo allenamento
    idx_to_delete = st.selectbox("Seleziona l'allenamento da eliminare:", [f"{i} - {w['Data']} - {w['Esercizio']}" for i, w in enumerate(st.session_state.workouts)])
    if st.button("Elimina allenamento selezionato"):
        idx = int(idx_to_delete.split(" - ")[0])
        st.session_state.workouts.pop(idx)
        st.success("Allenamento eliminato!")

    # Eliminare tutti gli allenamenti
    if st.button("Elimina tutti gli allenamenti"):
        st.session_state.workouts.clear()
        st.success("Tutti gli allenamenti sono stati eliminati!")

