from pymongo import MongoClient



def connect_to_mongo():
    """
    Connect to the MongoDB database.
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client['config_database']
    return db


def save_config_network(network_name, config_data):
    """
    Save any device config (switch/router) under a specific network collection.
    """
    db = None
    try:
        # Ensure config_data is a dictionary
        if not isinstance(config_data, dict):
            raise ValueError("Les données de configuration doivent être un dictionnaire.")
        db = connect_to_mongo()
        collection = db[network_name]  # collection = nom du réseau
        collection.insert_one(config_data)
        print(f"Configuration enregistrée dans le réseau '{network_name}'.")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de la configuration dans MongoDB : {e}")
        raise
    finally:
        if db is not None:
            db.client.close()


def prepare_for_mongo(device):
    import sys
    device = device.copy()
    interfaces = device["configs"]["interfaces"]
    # Convertir chaque Interface en dict si besoin
    for k, v in interfaces.items():
        if hasattr(v, '__dict__'):
            v_dict = v.__dict__
            # Convertir les gros entiers en str
            for key, value in v_dict.items():
                if isinstance(value, int) and abs(value) > sys.maxsize:
                    v_dict[key] = str(value)
            interfaces[k] = v_dict
        else:
            # Si c'est déjà un dict, vérifie aussi
            for key, value in v.items():
                if isinstance(value, int) and abs(value) > sys.maxsize:
                    v[key] = str(value)
    # Même chose pour le device lui-même
    for key, value in device.items():
        if isinstance(value, int) and abs(value) > sys.maxsize:
            device[key] = str(value)
    return device
