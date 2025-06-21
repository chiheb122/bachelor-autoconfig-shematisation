from ..Router import Router
from ..Switch import Switch



class DeviceFactory:
    """
    Classe utilitaire pour la création d'instances d'appareils réseau selon leur type.

    Méthodes :
        create_device(device_type, name, config) :
            Crée et retourne une instance d'appareil réseau (par exemple, Router ou Switch)
            en fonction du type spécifié. Lève une exception si le type n'est pas reconnu.

    Paramètres :
        device_type (str) : Le type d'appareil à créer ("router", "switch", etc.).
        name (str) : Le nom de l'appareil.
        config (dict) : La configuration associée à l'appareil.

    Exceptions :
        ValueError : Si le type d'appareil fourni n'est pas supporté.
    """
    @staticmethod
    def create_device(device_type, mac, name, config):
        if device_type.lower() == "router":
            return Router(mac, name, config)
        elif device_type.lower() == "switch":
            return Switch(mac, name, config)
        # Ajoute d'autres types ici si besoin
        else:
            raise ValueError(f"Type d'appareil inconnu : {device_type}")