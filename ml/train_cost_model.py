import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
import joblib

DATA_PATH = Path("synthetic_vehicle_service_logs.csv")
MODEL_PATH = Path("service_cost_model.pkl")

def load_data():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)

    # Drop rows with missing cost (just to be safe)
    df = df.dropna(subset=["cost"])

    return df

def preprocess_and_train(df):
    print("Preparing data...")

    features = [
        "vehicle_model",
        "service_type",
        "mileage",
        "mechanic_name",
    ]
    target = "cost"

    X = df[features]
    y = df[target]

    # Train-test split (not super important for synthetic data, but good practice)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.15, random_state=42
    )

    print("Building pipeline...")

    categorical_features = ["vehicle_model", "service_type", "mechanic_name"]
    numeric_features = ["mileage"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        max_depth=12
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    print("Training model...")
    pipeline.fit(X_train, y_train)

    # Print R² score just for info
    score = pipeline.score(X_test, y_test)
    print(f"Model R² score: {score:.3f}")

    print("Saving model...")
    joblib.dump(pipeline, MODEL_PATH)

    print(f"Model saved to {MODEL_PATH.resolve()}")

def main():
    df = load_data()
    preprocess_and_train(df)

if __name__ == "__main__":
    main()
