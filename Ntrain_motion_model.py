import os
import csv
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "ALL_DATA", "word_data")

MODEL_FILE = os.path.join(BASE_DIR, "MODELS", "word_model.pkl")


def load_data():
    X = []
    y = []
    
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            filepath = os.path.join(DATA_DIR, file)

            with open(filepath, "r") as f:
                reader = csv.reader(f)

                for row in reader:
                    label = row[0]
                    features = list(map(float, row[1:]))

                    X.append(features)
                    y.append(label)

    return np.array(X), np.array(y)


def main():
    print("Loading data...")
    X, y = load_data()

    print(f"Total samples: {len(X)}")
    print(f"Feature size: {len(X[0])}")

    print("Training model...")

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    joblib.dump(model, MODEL_FILE)

    print("Model saved as motion_model.pkl")


if __name__ == "__main__":
    main()