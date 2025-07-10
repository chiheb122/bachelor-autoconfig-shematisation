import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

class ConfigClassifier:
    def __init__(self, df):
        self.df = df.copy()
        self._prepare_data()
        self._train_model()
        
    def _prepare_data(self):
        # Séparation features/target
        self.X = self.df.drop(['filename', 'label'], axis=1)
        self.y = self.df['label']
        
        # Séparation train/test
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=0.2, random_state=42, stratify=self.y)
    
    def _train_model(self):
        # Modèle logistique simple
        self.model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
        self.model.fit(self.X_train, self.y_train)
    
    def show_top_features(self, top_n=10):
        """Affiche les coefficients les plus importants"""
        coefs = pd.DataFrame({
            'Feature': self.X.columns,
            'Coefficient': self.model.coef_[0]
        }).sort_values('Coefficient', key=abs, ascending=False).head(top_n)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Coefficient', y='Feature', data=coefs, palette='coolwarm')
        plt.title('Top Features les Plus Influentes')
        plt.xlabel('Coefficient')
        plt.tight_layout()
        plt.show()
        
        return coefs
    
    def evaluate(self):
        """Évaluation complète avec visualisations"""
        # 1. Distribution des classes
        self._plot_class_distribution()
        
        # 2. Matrice de confusion
        y_pred = self.model.predict(self.X_test)
        self._plot_confusion_matrix(y_pred)
        
        # 3. Rapport de classification
        print(classification_report(self.y_test, y_pred))
        
        # 4. Affichage des 5 premières instances
        print("\n5 premières instances du dataset:")
        print(self.df.head())
    
    def _plot_class_distribution(self):
        """Visualise la distribution des classes"""
        plt.figure(figsize=(6, 4))
        class_dist = self.y.value_counts(normalize=True)
        sns.barplot(x=class_dist.index, y=class_dist.values, palette='viridis')
        plt.title('Distribution des Classes')
        plt.ylabel('Probabilité')
        plt.ylim(0, 1)
        plt.show()
    
    def _plot_confusion_matrix(self, y_pred):
        """Affiche la matrice de confusion"""
        cm = confusion_matrix(self.y_test, y_pred)
        plt.figure(figsize=(6, 4))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=['incomplete_config', 'ok'],
                    yticklabels=['incomplete_config', 'ok'])
        plt.title('Matrice de Confusion')
        plt.xlabel('Prédit')
        plt.ylabel('Réel')
        plt.show()
    
    def predict(self, config_features):
        """Prédiction simple avec affichage des probabilités"""
        config_df = pd.DataFrame([config_features])
        proba = self.model.predict_proba(config_df)[0]
        pred = self.model.predict(config_df)[0]
        
        # Affichage graphique
        plt.figure(figsize=(6, 4))
        sns.barplot(x=self.model.classes_, y=proba, palette='viridis')
        plt.title(f'Probabilités de Prédiction ({pred})')
        plt.ylabel('Probabilité')
        plt.ylim(0, 1)
        plt.show()
        
        return {
            'prediction': pred,
            'probabilities': dict(zip(self.model.classes_, proba))
        }

# Exemple d'utilisation
if __name__ == "__main__":
    # 1. Chargement des données
    df = pd.read_csv("/Users/chiba/Desktop/TB/configExtract/src/IA/training/dataset.csv")
    
    # 2. Initialisation et entraînement
    clf = ConfigClassifier(df)
    
    # 3. Évaluation complète
    clf.evaluate()
    
    # 4. Affichage des features importantes
    top_features = clf.show_top_features()
    print("\nTop 5 des features les plus influentes:")
    print(top_features.head())
    
    # 5. Exemple de prédiction
    sample_config = {
        "has_hostname": 1,
        "has_enable_secret": 1,
        "has_line_vty": 1,
        "vty_has_login": 1,
        "has_ssh": 0,
        "no_ip_domain_lookup": 1,
        "has_routing_protocol": 0,
        "has_static_routes": 1,
        "ospf_network_configured": 1,
        "eigrp_network_configured": 1,
        "rip_network_configured": 1,
        "bgp_network_configured": 1,
        "has_management_ip": 0,
        "ip_addresses_overlap": 0
    }
    prediction = clf.predict(sample_config)
    print("\nRésultat de prédiction:", prediction)
