import time
import serial
import serial.tools.list_ports
import re
from pathlib import Path
import platform

# -------- PARAMÈTRES -------- #
BAUDRATE = 9600                    # Vitesse de communication série (standard Cisco)
TIMEOUT = 1                        # Délai d’attente pour la lecture série
PASSWORD_CONSOLE = None            # Mot de passe console (saisi dynamiquement)
PASSWORD_ENABLE = None             # Mot de passe enable (saisi dynamiquement)
CMD_DETECTION = 'show version'     # Commande pour identifier le type de l'appareil
CMD_CONFIG = 'show running-configs' # Commande pour extraire la configuration complète
CMD_NEIGHBORS = 'show cdp neighbors'
OUTPUT_FOLDER = 'dumps'            # Dossier de sortie (non utilisé ici, remplacé par configs/)
BASE_DIR = Path(__file__).resolve().parent.parent
HOSTNAME = None  # Variable pour stocker le nom d'hôte extrait de la configuration
# --------------------------- #

def list_serial_ports():
    """Retourne la liste des ports série disponibles sur la machine."""
    return [port.device for port in serial.tools.list_ports.comports()]

def connect_to_cisco_device():
    """Essaie de se connecter à tous les ports série disponibles et retourne le premier port actif avec une invite Cisco."""
    for port in list_serial_ports():
        try:
            print(f"🔌 Test de connexion sur {port}...")
            ser = serial.Serial(port, BAUDRATE, timeout=TIMEOUT)
            time.sleep(2)
            ser.read_all()

            # Send enter
            ser.write(b'\r')
           # Attendre un peu pour que l'appareil réponde
            time.sleep(1)
            output = ser.read_all().decode(errors='ignore')

            # Check if prompt looks Cisco-like
            if 'User Access Verification' in output or 'Password' in output or '>' in output or '#' in output:
                print(f"Appareil détecté sur {port}")
                return ser
            ser.close()
        except Exception as e:
            print(f"Erreur sur {port}: {e}")
    return None

def send(ser, cmd, timeout=30):
    """
    Envoie une commande et lit la sortie complète jusqu'à détection du prompt (finissant par #).
    Gère aussi les pages avec '--More--'.

    Args:
        ser: objet série
        cmd: commande à envoyer
        timeout: durée max d'attente
    """
    import re

    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write((cmd + '\r').encode())

    buffer = ''
    start_time = time.time()

    while time.time() - start_time < timeout:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += chunk

            # Pagination : envoyer espace
            if '--More--' in chunk or '--More--' in buffer[-20:]:
                ser.write(b' ')  # espace pour continuer
                time.sleep(0.2)

            # Fin de commande : ligne finissant par #
            if re.search(r'\n.*#\s*$', buffer):
                break

        time.sleep(0.1)

    return buffer


def identify_device_type(ser):
    """Identifie s’il s’agit d’un switch ou d’un routeur en envoyant des commandes spécifiques."""
    send(ser, '', 1)
    send(ser, PASSWORD_CONSOLE, 1)
    send(ser, 'enable', 1)
    send(ser, PASSWORD_ENABLE, 1)

    send(ser, 'end', 1)  # Quitte le mode configuration
    send(ser, 'terminal length 0', 1)  # Pour éviter le pagination
    # Test spécifique Switch
    vlan_response = send(ser, 'show vlan brief', 2)
    if "VLAN Name" in vlan_response:
        return 'switch', vlan_response

    # Si pas switch → on tente une commande routeur
    route_response = send(ser, 'show ip route', 2)
    if "Gateway of last resort" in route_response or "Codes:" in route_response:
        return 'router', route_response

    # Fallback : inconnu
    return 'unknown', vlan_response + "\n" + route_response

def extract_hostname_from_config(config_text):
    for line in config_text.splitlines():
        if line.strip().startswith("hostname"):
            return line.strip().split()[1]  # retourne juste le nom

def save_config(ser, device_type, output_path):
    """Extrait la configuration avec `show running-configs`, la nettoie, et l'enregistre dans un fichier .txt."""
    print("Extraction de la configuration...")
    config = send(ser, CMD_CONFIG, 6)
    cleaned_config = clean_config_output(config)
    global HOSTNAME
    HOSTNAME = extract_hostname_from_config(cleaned_config)
    filename = Path(output_path) / f"{device_type}_{HOSTNAME}_config.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(cleaned_config)
    print(f"Configuration sauvegardée dans {filename}")


def save_neighbors(ser, device_type, output_path):
    """Extrait les voisins CDP avec `show cdp neighbors` et les enregistre dans un fichier .txt."""
    print("Extraction des voisins CDP...")
    neighbors = send(ser, CMD_NEIGHBORS, 2)
    cleaned_neighbors = clean_config_output(neighbors)
    if not cleaned_neighbors.strip():
        print("Aucune donnée CDP reçue.")
        return

    filename = Path(output_path) / f"{device_type}_{HOSTNAME}_neighbors.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(cleaned_neighbors)
    print(f"Voisins CDP sauvegardés dans {filename}")


def clean_config_output(raw_output):
    """
    Nettoie la sortie brute de configuration d'un équipement réseau.

    Cette fonction prend en entrée une chaîne de caractères représentant la sortie brute d'une commande de configuration
    (par exemple, la sortie d'un "show running-configs" sur un équipement Cisco) et supprime les lignes non pertinentes
    ou inutiles pour obtenir un fichier de configuration plus lisible et exploitable. Les lignes ignorées incluent
    notamment les entêtes, les prompts de commande, et les commandes exécutées. Les lignes vides consécutives sont
    également réduites à une seule.

    Args:
        raw_output (str): La sortie brute de la configuration à nettoyer.

    Returns:
        str: La configuration nettoyée, prête à être exploitée ou sauvegardée.
    """
    """Supprime les lignes inutiles de la configuration brute pour obtenir un fichier plus lisible."""
    lines = raw_output.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        # Ignorer les lignes non utiles
        if line.lower().startswith('building configuration'):
            continue
        if line.lower().startswith('current configuration'):
            continue
        if line.lower().startswith('show running-configs'):
            continue
        if line.lower().startswith('show cdp neighbors'):
            continue
        if re.match(r'^.*#\s*show\s+running-configs$', line.lower()):
            continue
        if re.match(r'^\S+#$', line):  # prompt final type "Switch#"
            continue

        cleaned.append(line)

    # Supprimer les lignes vides consécutives
    final = []
    last_blank = False
    for line in cleaned:
        if line == '':
            if not last_blank:
                final.append(line)
            last_blank = True
        else:
            final.append(line)
            last_blank = False

    return '\n'.join(final)


def ask_network_folder():
    """Demande à l'utilisateur un nom de sous-dossier pour stocker les fichiers de configuration."""
    folder_name = input("Nom du dossier pour ce réseau (ex: resau1) : ").strip()
    full_path = BASE_DIR / "data/configs" / folder_name
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path



def ask_passwords():
    """Demande à l'utilisateur s'il souhaite saisir des mots de passe personnalisés pour la session."""
    global PASSWORD_CONSOLE, PASSWORD_ENABLE
    print("Configuration des mots de passe :")

    use_custom = input("Souhaitez-vous saisir des mots de passe personnalisés ? (y/n): ").strip().lower()
    if use_custom == 'y':
        PASSWORD_CONSOLE = input("Mot de passe console : ").strip()
        PASSWORD_ENABLE = input("Mot de passe enable : ").strip()
    else:
        PASSWORD_CONSOLE = 'cisco'
        PASSWORD_ENABLE = 'class'
        print("Utilisation des mots de passe par défaut : console='cisco', enable='class'")


def warn_permissions():
    """Affiche un message si l’utilisateur Linux n’est pas dans le groupe dialout pour accéder aux ports série."""
    if platform.system() == 'Linux':
        print("! Sur Linux, vous devez appartenir au groupe 'dialout' pour accéder au port série.")
        print("Exécutez : sudo usermod -aG dialout $USER puis déconnectez-vous/reconnectez-vous.")



def main():
    """Point d’entrée principal du script : configuration, détection, extraction et sauvegarde."""
    warn_permissions()
    ask_passwords()
    network_path = ask_network_folder()

    ser = connect_to_cisco_device()
    if not ser:
        print("Aucun appareil Cisco trouvé.")
        raise SystemExit("Aucune connexion série établie. Veuillez vérifier les connexions et réessayer.")
    

    try:
        device_type, version_info = identify_device_type(ser)
        print(f"Type d'appareil détecté : {device_type}")
        save_config(ser, device_type,network_path)
        save_neighbors(ser, device_type,network_path)
    finally:
        ser.close()
        print("Connexion série fermée.")

if __name__ == '__main__':
    main()
