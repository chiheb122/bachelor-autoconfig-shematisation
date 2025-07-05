import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

# Charger le dataset
df = pd.read_csv("dataset.csv")  # Le fichier doit être dans le même dossier

# Préparer les données
X = df.drop(columns=["filename", "label", "device_type"])
y = df["label"]

# Découpage en train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialiser le modèle de régression logistique
model = LogisticRegression(max_iter=1000)  # max_iter augmenté pour la convergence

# Entraînement
model.fit(X_train, y_train)

# Prédiction
y_pred = model.predict(X_test)

# Évaluation
print("✅ Évaluation du modèle Régression Logistique\n")
print(classification_report(y_test, y_pred))
print("🧮 Matrice de confusion :\n", confusion_matrix(y_test, y_pred))

# Affichage des poids (importance des features)
print("\n📊 Coefficients des features :")
for feature, coef in zip(X.columns, model.coef_[0]):
    print(f"{feature:<30} {coef:.4f}")