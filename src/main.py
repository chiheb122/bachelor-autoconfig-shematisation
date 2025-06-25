from src.app import TopologyGenerator
from src.configExtractor.pytermi import main

if __name__ == "__main__":
    try:
        main()  # Exécute la fonction principale pour démarrer l'extraction de configuration
        print("Extraction de la configuration terminée.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction de la configuration : {e}")
    # Après l'extraction, génère la topologie
    print("Génération de la topologie...")
    TopologyGenerator.run()
