import streamlit as st
import pandas as pd
import datetime
import os

CSV_FILE = "workouts.csv"

# Funzione per caricare i dati dal CSV
def load_workouts():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE)
            st.session_state.workouts = df.to_dict('records')
        except pd.errors.EmptyDataError:
            st.session_state.workouts = []
    else:
        st.session_state.workouts = []

# Funzione per salvare i dati sul CSV
def save_workouts():
    df = pd.DataFrame(st.session_state.workouts)
    df.to_csv(CSV_FILE, index=False)

# Inizializza storage (session_state)
if "workouts" not in st.session_state:
    load_workouts()

# Funzione per aggiungere una sessione di allenamento
def add_workout(date, split, exercise, weight_list, reps_list, rest_time, rep_range_per_set):
    num_sets = len(reps_list)
    total_reps = sum(reps_list)
    volume = sum([weight_list[i] * reps_list[i] for i in range(num_sets)])
    num_pauses = max(0, num_sets - 1)
    total_rest = rest_time * num_pauses
    density = volume / total_rest if total_rest > 0 else 0
    avg_load = volume / total_reps if total_reps > 0 else 0

    progress_score = (volume * 0.5) + (density * 0.3) + (avg_load * 0.2)

    range_achieved_per_set = [rep_range_per_set[i][0] <= reps_list[i] <= rep_range_per_set[i][1] for i in range(num_sets)]

    st.session_state.workouts.append({
        "Data": str(date),
        "Split": split,
        "Esercizio": exercise,
        "Peso per serie (kg)": str(weight_list),
        "Serie": num_sets,
        "Ripetizioni per serie": str(reps_list),
        "Ripetizioni totali": total_reps,
        "Recupero medio (s)": rest_time,
        "Volume": volume,
        "Densità": round(density, 2),
        "Carico medio per rep": round(avg_load, 2),
        "Progress Score": round(progress_score, 2),
        "Range raggiunto per serie": range_achieved_per_set
    })
    save_workouts()

# Funzione per calcolare feedback globale
def feedback(split, exercise):
    records = [w for w in st.session_state.workouts if w["Esercizio"] == exercise and w["Split"] == split]
    if not records:
        return "Non ci sono abbastanza dati per valutare la progressione."

    latest = records[-1]

    fb = f"Feedback per {exercise} ({latest['Data']}) nel split {split}:\n"
    for idx, achieved in enumerate(latest['Range raggiunto per serie']):
        fb += f"Serie {idx+1}: {'✅ Rientra nel range' if achieved else '❌ Fuori dal range'} (Peso: {latest['Peso per serie (kg)'].strip('[]').split(',')[idx]} kg)\n"

    fb += f"Progress Score: {latest['Progress Score']}"

    return fb

# ===================== STREAMLIT APP =====================

st.title("🏋️ Tracciamento Progressi in Palestra")

st.subheader("Inserisci un nuovo allenamento")
with st.form("workout_form"):
    date = st.date_input("Data allenamento", datetime.date.today())
    split = st.text_input("Nome dello Split", "Full Body")
    exercise = st.text_input("Esercizio", "Panca Piana")

    st.subheader("Peso e ripetizioni per serie e range per serie (max 5 serie)")
    weight_list = []
    reps_list = []
    rep_range_per_set = []
    for i in range(5):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            weight = st.number_input(f"Serie {i+1} Peso (kg)", min_value=0, value=0, key=f"weight_{i}")
        with col2:
            reps = st.number_input(f"Serie {i+1} Ripetizioni", min_value=0, value=0, key=f"rep_{i}")
        with col3:
            min_rep = st.number_input(f"Serie {i+1} min", min_value=0, value=8, key=f"min_{i}")
        with col4:
            max_rep = st.number_input(f"Serie {i+1} max", min_value=min_rep, value=12, key=f"max_{i}")

        if reps > 0 and weight > 0:
            reps_list.append(reps)
            weight_list.append(weight)
            rep_range_per_set.append((min_rep, max_rep))

    rest_time = st.number_input("Tempo medio di recupero tra le serie (s)", min_value=0, value=90)

    submitted = st.form_submit_button("Aggiungi")

    if submitted:
        if reps_list and weight_list:
            add_workout(date, split, exercise, weight_list, reps_list, rest_time, rep_range_per_set)
            st.success("Allenamento aggiunto!")
        else:
            st.warning("Inserisci almeno un peso e ripetizioni maggiori di zero per le serie.")

# Mostra storico allenamenti filtrato per esercizio
if st.session_state.workouts:
    df = pd.DataFrame(st.session_state.workouts)
    st.subheader("📊 Storico Allenamenti")

    split_scelta = st.selectbox("Seleziona uno Split per analisi", df["Split"].unique().tolist())
    esercizi = df[df["Split"] == split_scelta]["Esercizio"].unique().tolist()
    scelta = st.selectbox("Seleziona esercizio per analisi", esercizi)

    df_filtered = df[(df["Split"] == split_scelta) & (df["Esercizio"] == scelta)]
    st.dataframe(df_filtered)

    st.text(feedback(split_scelta, scelta))
