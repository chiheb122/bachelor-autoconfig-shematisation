import re
from src.models.Interface import Interface
from src.models.factory.DeviceFactory import DeviceFactory

def detect_device_type(config_lines):
    is_router = False
    is_switch = False

    for line in config_lines:
        line = line.lower().strip()

        if line.startswith("interface vlan") or "switchport" in line:
            is_switch = True
        if "router ospf" in line or "ip route" in line:
            is_router = True

    if is_router:
        return "router"
    if is_switch:
        return "switch"
    return "unknown"


def parse_config_to_json(config_path):
    config_lines = read_config_file(config_path)
    if not config_lines:
        raise ValueError("Le fichier de configuration est vide ou introuvable.")

    device_type = detect_device_type(config_lines)
    if device_type == "unknown":
        raise ValueError("Type de périphérique non reconnu dans le fichier.")

    parser = CiscoConfigParser(config_lines)

    interfaces = {}
    for iface_name, iface_data in parser.interfaces.items():
        iface = Interface(
            name=normalize_interface_name(iface_name),
            ip=iface_data.get("ip", ""),
            subnet_mask=iface_data.get("subnet_mask", ""),
            status=iface_data.get("status", "down"),
            vlan=iface_data.get("vlan", None),
            mac=iface_data.get("mac", ""),
            description=iface_data.get("description", "")
        )
        interfaces[iface.name] = iface

    return {
        "type": device_type,
        "name": parser.hostname or "Unknown",
        "mac": "00:11:22:33:44:55",  # Placeholder
        "config": {
            "interfaces": interfaces,
            "neighbors": parser.neighbors
        },
        "raw": "".join(config_lines)
    }


def normalize_interface_name(name: str) -> str:
    """
    Convertit les abréviations d'interface vers le format complet requis pour l'XML.
    Ex: g0/1, fas0/3, Gig0/2 → GigabitEthernet0/1, FastEthernet0/3, GigabitEthernet0/2
    """
    # Mapping des débuts possibles
    mapping = {
        "g": "GigabitEthernet",
        "gi": "GigabitEthernet",
        "gig": "GigabitEthernet",
        "f": "FastEthernet",
        "fa": "FastEthernet",
        "fas": "FastEthernet",
        "e": "Ethernet",
        "s": "Serial",
    }

    name = name.lower()

    # Trouver le préfixe et les chiffres
    match = re.match(r"([a-z]+)(\d+/\d+)", name)
    if match:
        prefix, numbers = match.groups()
        full_prefix = mapping.get(prefix, prefix.capitalize())
        return f"{full_prefix}{numbers}"
    else:
        return name  # si rien ne match, on retourne le nom d'origine

def parse_cdp_neighbors(output):
    with open(output, "r") as f:
        lines = f.readlines()

    neighbors = []
    for line in lines:
        # Ignorer l'en-tête ou ligne vide
        if not line.strip() or line.startswith("Device ID") or line.startswith("----"):
            continue

            # Regex robuste : capture Device ID, Local Interface, puis extrait le dernier champ comme Port ID
            parts = line.split()
            if len(parts) >= 6:
                device_id = parts[0]
                local_intf = normalize_interface_name("".join(parts[1:3]))  # ex: Gig 0/1
                port_id = normalize_interface_name("".join(parts[-2:]))     # ex: Fas 0/1
                neighbors.append({
                    "device_id": device_id,
                    "local_interface": local_intf,
                    "port_id": port_id
                })
    return neighbors



def read_config_file(file_path):
    """
    Lit un fichier de configuration  et retourne les lignes.
    """
    with open(file_path, "r") as file:
        return file.readlines() 

class CiscoConfigParser:
    def __init__(self, lines):
        self.lines = lines
        self.hostname = None
        self.interfaces = {}
        self.neighbors = {}
        self.parse()

    def parse(self):
        current_iface = None
        for line in self.lines:
            line = line.strip()
            if line.startswith("hostname"):
                self.hostname = line.split()[1]
            elif line.startswith("interface"):
                current_iface = line.split()[1]
                self.interfaces[current_iface] = {}
            elif line.startswith("ip address") and current_iface:
                self.interfaces[current_iface]["ip"] = line.split()[2]
                self.interfaces[current_iface]["subnet_mask"] = line.split()[3] if len(line.split()) > 3 else ""
            elif line.startswith("shutdown") and current_iface:
                self.interfaces[current_iface]["status"] = "down"
            elif line.startswith("no shutdown") and current_iface:
                self.interfaces[current_iface]["status"] = "up"
            elif line.startswith("switchport access vlan") and current_iface:
                self.interfaces[current_iface]["vlan"] = int(line.split()[-1])
            elif line.startswith("mac address") and current_iface:
                self.interfaces[current_iface]["mac"] = line.split()[2]
            elif line.startswith("description") and current_iface:
                self.interfaces[current_iface]["description"] = " ".join(line.split()[1:])
            elif line.lower().startswith("cdp entry") or "show cdp neighbors" in line:
                pass  # Ajoute plus tard pour les liaisons

    def __str__(self):
        return f"Hostname: {self.hostname}, Interfaces: {self.interfaces} \nNeighbors: {self.neighbors}"

