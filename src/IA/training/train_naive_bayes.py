import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import classification_report, confusion_matrix

# Charger le dataset
df = pd.read_csv("dataset.csv")  # Assure-toi que dataset.csv est dans le même dossier

# Séparer les features des colonnes inutiles
X = df.drop(columns=["filename", "label", "device_type"])
y = df["label"]

# Découpage en train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialisation et entraînement du modèle
model = BernoulliNB()
model.fit(X_train, y_train)

# Évaluation
y_pred = model.predict(X_test)

print("Évaluation du modèle Naïve Bayes\n")
print(classification_report(y_test, y_pred))
print("Matrice de confusion :\n", confusion_matrix(y_test, y_pred))

# Facultatif : sauvegarde du modèle (si besoin avec joblib)
# from joblib import dump
# dump(model, "naive_bayes_config_model.joblib")
