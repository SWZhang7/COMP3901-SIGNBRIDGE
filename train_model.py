import os
import glob
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib

DATA_FOLDER = "data"
MODEL_FILE = "sign_model.pkl"


def load_data():
    all_rows = []

    csv_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))

    if not csv_files:
        print("No CSV files found in data folder.")
        return None

    for file in csv_files:
        df = pd.read_csv(file, header=None)
        all_rows.append(df)

    combined = pd.concat(all_rows, ignore_index=True)
    return combined


def main():
    data = load_data()

    if data is None:
        return

    X = data.iloc[:, 1:]
    y = data.iloc[:, 0]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_FILE)
    print(f"Model saved as {MODEL_FILE}")


if __name__ == "__main__":
    main()