from src.app import main_menu

if __name__ == "__main__":
    try:
        # Lancer le menu principal de l'application
        main_menu()
    except KeyboardInterrupt:
        print("\n\nProgramme interrompu par l'utilisateur. Au revoir !")
    except ImportError as e:
        print(f"Erreur d'importation : {e}")
        print("Vérifiez que toutes les dépendances sont installées.")
    except Exception as e:
        print(f"Erreur inattendue : {e}")




