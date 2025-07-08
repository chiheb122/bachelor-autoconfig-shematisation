# Importations des bibliothèques nécessaires
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

# --- Configuration de Matplotlib et Seaborn pour des graphiques clairs ---
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6) # Taille par défaut des figures
plt.rcParams['figure.dpi'] = 100       # Résolution des figures

# Charge un DataFrame depuis un fichier CSV
def load_dataset(path):
    try:
        df = pd.read_csv(path)
        print(f"Dataset '{path}' chargé ({df.shape[0]} lignes).")
        return df
    except FileNotFoundError:
        print(f"Fichier '{path}' introuvable.")
        return None

# Affiche un aperçu rapide du DataFrame
def quick_overview(df):
    print(df.head())
    print(df.info())
    print(df['label'].value_counts(normalize=True))

# Affiche la répartition des classes
def plot_class_distribution(df):
    class_counts = df['label'].value_counts(normalize=True)
    plt.figure(figsize=(7, 5))
    sns.barplot(x=class_counts.index, y=class_counts.values, palette='viridis')
    plt.title('Probabilité A Priori des Classes')
    plt.xlabel('Classe')
    plt.ylabel('Probabilité')
    plt.ylim(0, 1)
    plt.show()

# Classe utilitaire pour tout le pipeline ML
class ConfigClassifier:
    # Initialise et entraîne le modèle
    def __init__(self, df, categorical_features=['vtp_mode']):
        self.label_encoder = LabelEncoder()
        df = df.copy()
        df['label_encoded'] = self.label_encoder.fit_transform(df['label'])
        X = df.drop(['filename', 'label', 'label_encoded'], axis=1)
        y = df['label_encoded']
        self.categorical_features = categorical_features
        self.numerical_features = X.select_dtypes(include=np.number).columns.tolist()
        self.preprocessor = ColumnTransformer(
            transformers=[('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)],
            remainder='passthrough'
        )
        X_processed = self.preprocessor.fit_transform(X)
        self.feature_names = list(self.preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_features)) + self.numerical_features
        X_train, X_test, y_train, y_test = train_test_split(X_processed, y, test_size=0.2, random_state=42, stratify=y)
        self.model = LogisticRegression(random_state=42, solver='liblinear', max_iter=1000)
        self.model.fit(X_train, y_train)
        self.X_test, self.y_test = X_test, y_test
        print("Modèle entraîné.")

    # Prédit la classe et les probabilités pour un exemple
    def predict(self, example_dict):
        df = pd.DataFrame([example_dict])
        X = self.preprocessor.transform(df)
        pred_proba = self.model.predict_proba(X)[0]
        pred_label_encoded = self.model.predict(X)[0]
        pred_label = self.label_encoder.inverse_transform([pred_label_encoded])[0]
        # AffiCHER un graphique des probabilités
        plt.figure(figsize=(8, 5))
        sns.barplot(x=self.label_encoder.classes_, y=pred_proba, palette='viridis')
        plt.title(f'Probabilités de Classe pour {pred_label}')
        plt.xlabel('Classe')
        plt.ylabel('Probabilité')
        plt.xticks(rotation=45)
        plt.show()
        print(f"Prédiction : {pred_label} avec probabilités {pred_proba}")
        # Retourne la prédiction et les probabilités
        if len(pred_proba) == 0:
            print("Aucune probabilité prédite, vérifiez l'entrée.")
            return None
        return {
            "prediction": pred_label,
            "probabilities": {label: float(pred_proba[i]) for i, label in enumerate(self.label_encoder.classes_)}
        }

    # Affiche les coefficients les plus influents
    def show_top_features(self, top_n=15):
        coefs = self.model.coef_[0]
        feature_coefs = pd.DataFrame({'Feature': self.feature_names, 'Coefficient': coefs})
        feature_coefs['Abs'] = np.abs(feature_coefs['Coefficient'])
        feature_coefs_sorted = feature_coefs.sort_values(by='Abs', ascending=False)
        print("\n📊 Top features :")
        print(feature_coefs_sorted.head(top_n)[['Feature', 'Coefficient']])
        plt.figure(figsize=(10, 8))
        sns.barplot(x='Coefficient', y='Feature', data=feature_coefs_sorted.head(top_n), palette='coolwarm')
        plt.title('Top Caractéristiques les Plus Influentes')
        plt.xlabel('Influence')
        plt.ylabel('Caractéristique')
        plt.show()

    # Évalue le modèle sur le test set
    def evaluate(self):
        y_pred = self.model.predict(self.X_test)
        print("\nRapport de classification :\n")
        print(classification_report(self.y_test, y_pred, target_names=self.label_encoder.classes_))
        conf_matrix = confusion_matrix(self.y_test, y_pred)
        print("Matrice de confusion :\n", conf_matrix)
        plt.figure(figsize=(6, 4))
        sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
                    xticklabels=self.label_encoder.classes_, yticklabels=self.label_encoder.classes_)
        plt.xlabel('Prédit')
        plt.ylabel('Réel')
        plt.title('Matrice de Confusion')
        plt.show()

# --------- MAIN SCRIPT ---------
if __name__ == "__main__":
    print("# --- Début de l'exécution du script ---")
    df = load_dataset("/Users/chiba/Desktop/TB/configExtract/src/IA/training/dataset.csv")
    if df is None:
        exit(1)
    quick_overview(df)
    plot_class_distribution(df)
    clf = ConfigClassifier(df)
    clf.show_top_features()
    clf.evaluate()

    # Exemple custom à prédire
    new_example = {
    "has_hostname": 1,
    "has_secretPass": 1,
    "has_dhcp_server": 1,
    "ip_addresses_overlap": 1,
    "has_nat_configured": 1,
    "vtp_password_configured": 0,
    "Has_routing_protocole": 1,
    "has_description_on_interfaces": 1,
    "dhcp_pool_configured": 0,
    "has_cdp_enabled": 1,
    "no_ip_domain_lookup": 0,
    "has_ssh": 1,
    "vtp_domain_configured": 0,
    "vtp_mode": "none",
    "has_vlan": 0,
    "missing_network_on_routing": 1,
    "acl_configured": 1,
    "has_switchportonVlan": 0,
    "vlan_interface_management_ip": 0
    }
    result = clf.predict(new_example)
    print("\nRésultat prédiction custom :", result)
    print("\n# --- Fin de l'exécution du script ---")