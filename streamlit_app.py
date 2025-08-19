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
def add_workout(date, split, exercise, weight, reps_list, rest_time):
    total_reps = sum(reps_list)
    volume = weight * total_reps
    num_sets = len(reps_list)
    num_pauses = max(0, num_sets - 1)
    total_rest = rest_time * num_pauses
    density = volume / total_rest if total_rest > 0 else 0
    avg_load = volume / total_reps if total_reps > 0 else 0

    progress_score = (volume * 0.5) + (density * 0.3) + (avg_load * 0.2)

    st.session_state.workouts.append({
        "Data": str(date),
        "Split": split,
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
    save_workouts()

# Funzione per calcolare feedback globale
def feedback(split, exercise):
    records = [w for w in st.session_state.workouts if w["Esercizio"] == exercise and w["Split"] == split]
    if len(records) < 2:
        return "Non ci sono abbastanza dati per valutare la progressione."

    latest = records[-1]
    prev = records[-2]

    diff_score = latest["Progress Score"] - prev["Progress Score"]

    fb = f"Progressione globale per {exercise} ({latest['Data']}) nel split {split}:\n"
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
    split = st.text_input("Nome dello Split", "Full Body")
    exercise = st.text_input("Esercizio", "Panca Piana")
    weight = st.number_input("Peso (kg)", min_value=0, value=60)
    n_sets = st.number_input("Numero di serie", min_value=1, value=3)

    reps_list = []
    for i in range(int(n_sets)):
        r = st.number_input(f"Ripetizioni serie {i+1}", min_value=1, value=10, key=f"rep_{i}")
        reps_list.append(r)

    rest_time = st.number_input("Tempo medio di recupero tra le serie (s)", min_value=0, value=90)
    submitted = st.form_submit_button("Aggiungi")

    if submitted:
        add_workout(date, split, exercise, weight, reps_list, rest_time)
        st.success("Allenamento aggiunto!")

# Mostra storico allenamenti filtrato per esercizio
if st.session_state.workouts:
    df = pd.DataFrame(st.session_state.workouts)
    st.subheader("📊 Storico Allenamenti")

    split_scelta = st.selectbox("Seleziona uno Split per analisi", df["Split"].unique().tolist())
    esercizi = df[df["Split"] == split_scelta]["Esercizio"].unique().tolist()
    scelta = st.selectbox("Seleziona esercizio per analisi", esercizi)

    # Filtra solo gli allenamenti relativi all'esercizio selezionato
    df_filtered = df[(df["Split"] == split_scelta) & (df["Esercizio"] == scelta)]
    st.dataframe(df_filtered)

    st.text(feedback(split_scelta, scelta))

    st.subheader("📈 Progressione Volume")
    chart_data = df_filtered[["Data", "Volume"]]
    st.line_chart(chart_data.set_index("Data"))

    st.subheader("⚡ Progressione Densità")
    chart_density = df_filtered[["Data", "Densità"]]
    st.line_chart(chart_density.set_index("Data"))

    st.subheader("🏋️‍♂️ Progressione Carico Medio")
    chart_load = df_filtered[["Data", "Carico medio per rep"]]
    st.line_chart(chart_load.set_index("Data"))

    st.subheader("🌟 Progressione Globale (Progress Score)")
    chart_score = df_filtered[["Data", "Progress Score"]]
    st.line_chart(chart_score.set_index("Data"))

    st.subheader("🗑️ Gestione Allenamenti")
    idx_to_delete = st.selectbox("Seleziona l'allenamento da eliminare", [f"{i} - {w['Data']} - {w['Split']} - {w['Esercizio']}" for i, w in enumerate(df_filtered.to_dict('records'))])
    if st.button("Elimina allenamento selezionato"):
        # Trova l'indice originale nel session_state
        record_to_delete = df_filtered.to_dict('records')[int(idx_to_delete.split(' - ')[0])]
        original_idx = next(i for i, w in enumerate(st.session_state.workouts) if w == record_to_delete)
        st.session_state.workouts.pop(original_idx)
        save_workouts()
        st.success("Allenamento eliminato!")

    if st.button("Elimina tutti gli allenamenti"):
        st.session_state.workouts.clear()
        save_workouts()
        st.success("Tutti gli allenamenti sono stati eliminati!")
