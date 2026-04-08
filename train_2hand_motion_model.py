import os
import csv
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "ALL_DATA", "phrase_data")
MODEL_FILE = os.path.join(BASE_DIR, "MODELS", "phrase_model.pkl")


def load_data():
    X = []
    y = []
    lengths = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            filepath = os.path.join(DATA_DIR, file)

            with open(filepath, "r", newline="") as f:
                reader = csv.reader(f)

                for row_num, row in enumerate(reader, start=1):
                    if not row:
                        continue

                    label = row[0]
                    features = list(map(float, row[1:]))

                    X.append(features)
                    y.append(label)
                    lengths.append(len(features))

    unique_lengths = sorted(set(lengths))
    print("Detected feature lengths:", unique_lengths)

    if len(unique_lengths) != 1:
        raise ValueError(
            f"Inconsistent feature lengths found: {unique_lengths}. "
            "Your 2-hand motion samples are not all the same size."
        )

    return np.array(X, dtype=np.float32), np.array(y)


def main():
    print("Loading 2-hand motion data...")
    X, y = load_data()

    print(f"Total samples: {len(X)}")
    print(f"Feature size: {len(X[0])}")

    print("Training 2-hand motion model...")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_FILE)

    print(f"Model saved as {MODEL_FILE}")


if __name__ == "__main__":
    main()