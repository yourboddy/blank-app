import datetime

class WorkoutEntry:
    def __init__(self, exercise, weight, reps, sets, duration):
        self.date = datetime.date.today()
        self.exercise = exercise
        self.weight = weight
        self.reps = reps
        self.sets = sets
        self.duration = duration  # in minuti

    @property
    def total_reps(self):
        return self.reps * self.sets

    @property
    def volume(self):
        return self.weight * self.total_reps

    @property
    def density(self):
        return self.volume / self.duration if self.duration > 0 else 0

    @property
    def avg_load_per_rep(self):
        return self.volume / self.total_reps if self.total_reps > 0 else 0

    def summary(self):
        return {
            "Esercizio": self.exercise,
            "Data": str(self.date),
            "Volume": self.volume,
            "Densità": round(self.density, 2),
            "Ripetizioni Totali": self.total_reps,
            "Carico medio per rep": round(self.avg_load_per_rep, 2)
        }


class ProgressTracker:
    def __init__(self):
        self.history = []

    def add_entry(self, entry):
        self.history.append(entry)

    def feedback(self, exercise):
        records = [e for e in self.history if e.exercise == exercise]
        if len(records) < 2:
            return "Non ci sono abbastanza dati per valutare la progressione."

        latest = records[-1]
        prev = records[-2]

        diff_volume = latest.volume - prev.volume
        diff_density = latest.density - prev.density

        feedback = f"Progressione per {exercise} ({latest.date}):\n"
        feedback += f"- Volume: {latest.volume} ({'+' if diff_volume>=0 else ''}{diff_volume})\n"
        feedback += f"- Densità: {latest.density:.2f} ({'+' if diff_density>=0 else ''}{diff_density:.2f})\n"

        if diff_volume > 0:
            feedback += "Ottimo! Hai aumentato il volume.\n"
        elif diff_volume < 0:
            feedback += "Attenzione: volume in calo.\n"

        return feedback


# ESEMPIO D'USO
tracker = ProgressTracker()

# Inserisco 2 sessioni di panca piana
session1 = WorkoutEntry("Panca Piana", weight=60, reps=10, sets=3, duration=30)
session2 = WorkoutEntry("Panca Piana", weight=65, reps=10, sets=3, duration=30)

tracker.add_entry(session1)
tracker.add_entry(session2)

print(session1.summary())
print(session2.summary())
print(tracker.feedback("Panca Piana"))


