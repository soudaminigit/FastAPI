# train_model.py

import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def train():
    df = pd.read_csv("https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv")
    df = df[["Pclass", "Sex", "Age", "SibSp",  "Fare", "Survived"]]
    df.dropna(inplace=True)

    df["Sex"] = LabelEncoder().fit_transform(df["Sex"])
    X = df.drop("Survived", axis=1)
    y = df["Survived"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    with open("models/model.pkl", "wb") as f:
        pickle.dump(model, f)

    with open("models/features.pkl", "wb") as f:
        pickle.dump(X.columns.tolist(), f)

if __name__ == "__main__":
    train()
