from src.app import TopologyGenerator
from src.config.extract.pytermi import main

if __name__ == "__main__":
    try:
        response = input("Avez-vous des configurations à extraire ? (oui/non)")
        while response.lower() == "oui":
            main()  # Relance l'extraction de configuration si l'utilisateur le souhaite
            response = input("Avez-vous d'autres configurations à extraire ? (oui/non)")
        # Si l'utilisateur ne souhaite pas extraire d'autres configurations, on termine le programme
        print("Extraction de la configuration terminée.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de l'extraction de la configuration : {e}")
    # Après l'extraction, génère la topologie
    print("Génération de la topologie...")
    TopologyGenerator.run()
