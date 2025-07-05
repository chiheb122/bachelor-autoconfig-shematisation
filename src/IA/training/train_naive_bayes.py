# Importations des bibliothèques nécessaires
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO # Pour le dataset de fallback

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# --- Configuration de Matplotlib et Seaborn pour des graphiques clairs ---
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6) # Taille par défaut des figures
plt.rcParams['figure.dpi'] = 100       # Résolution des figures

print("# --- Début de l'exécution du script ---")

# --- 1. Chargement et Première Exploration des Données ---
print("\n## Étape 1 : Chargement et Première Exploration des Données")

# Tenter de charger le dataset.csv
try:
    df = pd.read_csv("dataset.csv")
    print("Dataset 'dataset.csv' chargé avec succès.")

except FileNotFoundError:
    print("Le fichier 'dataset.csv' est introuvable.")

print("\n### 1.1. Aperçu des 5 premières lignes du DataFrame :")
print(df.head())

print("\n### 1.2. Informations sur les colonnes et les types de données :")
df.info()

print("\n### 1.3. Répartition des classes 'ok'/'incomplete_config' (Probabilité A Priori) :")
class_counts = df['label'].value_counts(normalize=True)
print(class_counts)

plt.figure(figsize=(7, 5))
sns.barplot(x=class_counts.index, y=class_counts.values, palette='viridis')
plt.title('1.3. Probabilité A Priori des Classes')
plt.xlabel('Classe')
plt.ylabel('Probabilité')
plt.ylim(0, 1)
plt.show()
print("**Explication :** Cette visualisation montre la probabilité de base qu'une configuration appartienne à une classe ou l'autre, avant d'analyser ses caractéristiques spécifiques. C'est le point de départ pour le modèle.")


# --- 2. Préparation et Prétraitement des Données ---
print("\n## Étape 2 : Préparation et Prétraitement des Données")

df_processed = df.copy()

# 2.1. Encodage de la variable cible 'label'
label_encoder = LabelEncoder()
df_processed['label_encoded'] = label_encoder.fit_transform(df_processed['label'])
print(f"Mapping des labels : {list(label_encoder.classes_)} -> {list(label_encoder.transform(label_encoder.classes_))}")

# 2.2. Séparation des caractéristiques (X) et de la variable cible (y)
X = df_processed.drop(['filename', 'label', 'label_encoded'], axis=1)
y = df_processed['label_encoded']
print(f"\n### 2.2. Taille des caractéristiques (X) avant One-Hot Encoding : {X.shape}")
print(f"### 2.2. Taille de la variable cible (y) : {y.shape}")

# 2.3. Gestion des variables catégorielles avec One-Hot Encoding
categorical_features = ['vtp_mode']
numerical_features = X.select_dtypes(include=np.number).columns.tolist()

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ],
    remainder='passthrough'
)
X_processed = preprocessor.fit_transform(X)

# Récupérer les noms des caractéristiques après prétraitement
one_hot_feature_names = preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)
feature_names_processed = list(one_hot_feature_names) + numerical_features

print("\n### 2.3. Aperçu des caractéristiques après prétraitement (première ligne) :")
X_processed_sample_df = pd.DataFrame(X_processed[0:1], columns=feature_names_processed)
print(X_processed_sample_df.T.rename(columns={0: 'Valeur'}))

# 2.4. Division des données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)
print(f"\n### 2.4. Taille de l'ensemble d'entraînement (X_train) : {X_train.shape}")
print(f"### 2.4. Taille de l'ensemble de test (X_test) : {X_test.shape}")


# --- 3. Construction et Entraînement du Modèle ---
print("\n## Étape 3 : Construction et Entraînement du Modèle")

# 3.1. Initialiser le modèle de régression logistique
model = LogisticRegression(random_state=42, solver='liblinear', max_iter=1000)

# 3.2. Entraînement du modèle
model.fit(X_train, y_train)
print("✅ Modèle de Régression Logistique entraîné avec succès !")

# 3.3. Affichage des poids (coefficients) et du biais
coefficients = model.coef_[0]
intercept = model.intercept_[0]
print(f"\n### 3.3. Biais (Intercept) du modèle : {intercept:.4f}")
print("\n### 3.3. Coefficients (poids) des caractéristiques (Top 10) :")
feature_coefs = pd.DataFrame({'Feature': feature_names_processed, 'Coefficient': coefficients})
feature_coefs['Absolute_Coefficient'] = np.abs(feature_coefs['Coefficient'])
feature_coefs_sorted = feature_coefs.sort_values(by='Absolute_Coefficient', ascending=False)
print(feature_coefs_sorted.head(10))


# --- 4. Démonstration du Calcul des Probabilités pour une Configuration Spécifique ---
print("\n## Étape 4 : Démonstration du Calcul des Probabilités pour une Configuration Spécifique")

# 4.1. Sélection d'une configuration d'exemple
sample_index_in_test = 0
sample_config_X = X_test[sample_index_in_test].reshape(1, -1)

print("\n### 4.1. Caractéristiques de la configuration d'exemple :")
sample_config_df = pd.DataFrame(sample_config_X, columns=feature_names_processed)
print(sample_config_df.T.rename(columns={0: 'Valeur'}))

true_label_encoded = y_test[sample_index_in_test]
true_label = label_encoder.inverse_transform([true_label_encoded])[0]
print(f"\n### 4.1. Vraie étiquette pour cette configuration : '{true_label}'")

# 4.2. Calcul du Score Logit (z)
z_score = intercept + np.dot(sample_config_X, coefficients)[0]
print(f"\n### 4.2. Calcul du Score Logit (z) :")
print(f"  Biais (Intercept) : {intercept:.4f}")
print(f"  Somme pondérée des caractéristiques : {np.dot(sample_config_X, coefficients)[0]:.4f}")
print(f"  Score Logit (z) : {z_score:.4f}")

# 4.3. Transformation du Score Logit en Probabilité (Fonction Sigmoïde)
prob_ok_calculated = 1 / (1 + np.exp(-z_score))
prob_incomplete_calculated = 1 - prob_ok_calculated
print(f"\n### 4.3. Application de la Fonction Sigmoïde :")
print(f"  P(label = 'ok' | Caractéristiques) = 1 / (1 + e^(-{z_score:.4f})) = {prob_ok_calculated:.4f}")
print(f"  P(label = 'incomplete_config' | Caractéristiques) = 1 - {prob_ok_calculated:.4f} = {prob_incomplete_calculated:.4f}")

model_probabilities = model.predict_proba(sample_config_X)[0]
prob_incomplete_model = model_probabilities[label_encoder.transform(['incomplete_config'])[0]]
prob_ok_model = model_probabilities[label_encoder.transform(['ok'])[0]]
print(f"\n### 4.3. Probabilités obtenues directement du modèle (predict_proba) :")
print(f"  P('incomplete_config') du modèle : {prob_incomplete_model:.4f}")
print(f"  P('ok') du modèle : {prob_ok_model:.4f}")
print(f"  Vérification : Les probabilités calculées manuellement et par le modèle sont très similaires : {np.isclose(prob_ok_calculated, prob_ok_model)}")

# Visualisation des Probabilités Prédites
probabilities_data = pd.DataFrame({
    'Classe': ['incomplete_config', 'ok'],
    'Probabilité': [prob_incomplete_calculated, prob_ok_calculated]
})
plt.figure(figsize=(7, 5))
sns.barplot(x='Classe', y='Probabilité', data=probabilities_data, palette='coolwarm')
plt.title(f'4.3. Probabilités Prédites pour la Configuration d\'Exemple (Vraie: {true_label})')
plt.xlabel('Classe')
plt.ylabel('Probabilité')
plt.ylim(0, 1)
plt.show()
print("**Explication :** Ce graphique montre la confiance du modèle pour chaque classe. Plus la barre est haute, plus la confiance est forte.")

# 4.4. Décision de Classification basée sur le Seuil
predicted_class_value = 1 if prob_ok_calculated >= 0.5 else 0
predicted_label = label_encoder.inverse_transform([predicted_class_value])[0]
print(f"\n### 4.4. Décision de Classification :")
print(f"  Seuil de décision : 0.5")
print(f"  Probabilité de 'ok' : {prob_ok_calculated:.4f}")
print(f"  Prédiction finale pour cette configuration : '{predicted_label}'")
print(f"  Le modèle a-t-il prédit correctement par rapport à la vraie étiquette ('{true_label}') ? {'Oui' if predicted_label == true_label else 'Non'}")


# --- 5. Évaluation Globale du Modèle ---
print("\n## Étape 5 : Évaluation Globale du Modèle")

# 5.1. Prédiction sur l'ensemble de test
y_pred = model.predict(X_test)

# 5.2. Rapport de Classification
print("\n✅ Évaluation du modèle Régression Logistique\n")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# 5.3. Matrice de Confusion
conf_matrix = confusion_matrix(y_test, y_pred)
print("🧮 Matrice de confusion :\n", conf_matrix)

plt.figure(figsize=(6, 4))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.xlabel('Prédit')
plt.ylabel('Réel')
plt.title('5.3. Matrice de Confusion')
plt.show()
print("\n**Interprétation :**")
print("- **True Positives (VP)** : Le modèle a prédit 'ok' et c'était 'ok'.")
print("- **True Negatives (VN)** : Le modèle a prédit 'incomplete_config' et c'était 'incomplete_config'.")
print("- **False Positives (FP)** : Le modèle a prédit 'ok' mais c'était 'incomplete_config' (erreur de Type I).")
print("- **False Negatives (FN)** : Le modèle a prédit 'incomplete_config' mais c'était 'ok' (erreur de Type II).")


# --- 6. Interprétation des Coefficients du Modèle ---
print("\n## Étape 6 : Interprétation des Coefficients du Modèle")

print("\n📊 Coefficients des features (Top 15 les plus influents) :")
for index, row in feature_coefs_sorted.head(15).iterrows():
    print(f"{row['Feature']:<30} {row['Coefficient']:.4f}")

# Visualisation des coefficients
plt.figure(figsize=(10, 8))
sns.barplot(x='Coefficient', y='Feature', data=feature_coefs_sorted.head(15), palette='coolwarm')
plt.title('6.2. Top 15 des Caractéristiques les Plus Influentes')
plt.xlabel('Influence sur la probabilité d\'être "ok"')
plt.ylabel('Caractéristique')
plt.show()
print("\n**Explication :**")
print("- Les barres vers la droite (coefficients positifs) indiquent que la caractéristique augmente la probabilité que la config soit 'ok'.")
print("- Les barres vers la gauche (coefficients négatifs) indiquent que la caractéristique augmente la probabilité que la config soit 'incomplete_config'.")
print("- La longueur de la barre (valeur absolue) montre la force de l'influence.")

print("\n# --- Fin de l'exécution du script ---")