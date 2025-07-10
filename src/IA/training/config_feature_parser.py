import re
import os
import pandas as pd



# Déclaration EXPLICITE de toutes les features avec leur ordre et valeur par défaut
FEATURE_TEMPLATE = {
    "filename": "",
    # Core features
    "has_hostname": 0,
    "has_enable_secret": 0,
    "has_line_vty": 0,
    "vty_has_login": 0,
    "has_ssh": 0,
    "no_ip_domain_lookup": 0,
    # Routing features
    "has_routing_protocol": 0,
    "has_static_routes": 0,
    "ospf_network_configured": 1,  # 1 par défaut (pas d'OSPF = OK)
    "eigrp_network_configured": 1,
    "rip_network_configured": 1,
    "bgp_network_configured": 1,
    # Management
    "has_management_ip": 0,
    # Advanced checks
    "ip_addresses_overlap": 0,
    # Label (DOIT être la dernière colonne)
    "label": ""
}


def is_config_ok(features):
    # Critères fondamentaux pour une config de base sécurisée
    core_security = [
        features["has_hostname"],
        features["has_enable_secret"],
        features["has_ssh"] or (features["has_line_vty"] and features["vty_has_login"]),
    ]
    
    # Vérification spécifique au routage
    routing_ok = True
    if features["has_routing_protocol"]:
        routing_ok = all([
            features["ospf_network_configured"],
            features["eigrp_network_configured"],
            features["rip_network_configured"],
            features["bgp_network_configured"]
        ])
    
    return "ok" if all(core_security) and routing_ok else "incomplete_config"

def extract_config_features(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        with open(config_path, "r", encoding="latin-1") as f:
            lines = [line.strip() for line in f if line.strip()]

    features = FEATURE_TEMPLATE.copy()
    features["filename"] = os.path.basename(config_path)
    # Détection des sections
    current_section = None
    routing_protocol = None
    
    for line in lines:
            # Hostname
            if "hostname" in line and not any(x in line for x in ["-", "router", "switch"]):
                features["has_hostname"] = 1
            
            # Enable secret
            if "enable secret" in line:
                features["has_enable_secret"] = 1
            
            # SSH
            if any(x in line.lower() for x in ["crypto key", "ip ssh", "ssh version"]):
                features["has_ssh"] = 1
            
            # Domain lookup
            if "no ip domain-lookup" in line:
                features["no_ip_domain_lookup"] = 1
            
            # VTY lines
            if line.startswith("line vty"):
                features["has_line_vty"] = 1
                current_section = "vty"
            elif current_section == "vty" and "login" in line:
                features["vty_has_login"] = 1
            
            # Static routes
            if line.startswith("ip route"):
                features["has_static_routes"] = 1
            
            # Routing protocols
            if line.startswith("router "):
                features["has_routing_protocol"] = 1
                routing_protocol = line.split()[1]
                if routing_protocol in ["ospf", "eigrp", "rip", "bgp"]:  # Only reset for known protocols
                    features[f"{routing_protocol}_network_configured"] = 0
            
            # Network statements
            if line.startswith("network ") and routing_protocol:
                features[f"{routing_protocol}_network_configured"] = 1
            
            # Management IP
            if "interface vlan" in line or "interface management" in line:
                current_section = "management"
            elif current_section == "management" and "ip address" in line:
                features["has_management_ip"] = 1
            
            # IP overlap detection
            ip_addresses = set()
            if "ip address" in line and "dhcp" not in line:
                ip_match = re.search(r"ip address (\d+\.\d+\.\d+\.\d+)", line)
                if ip_match:
                    ip = ip_match.group(1)
                    if ip in ip_addresses:
                        features["ip_addresses_overlap"] = 1
                    ip_addresses.add(ip)
        
    features["label"] = is_config_ok(features)
    return features

def parse_folder_to_csv(folder_path, output_csv="dataset.csv"):
    data = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt") and "config" in file.lower():
            features = extract_config_features(os.path.join(folder_path, file))
            data.append(features)
    
    pd.DataFrame(data).to_csv(output_csv, index=False)
    print(f"Dataset généré : {output_csv}")
    return data

# Exemple d'utilisation
if __name__ == "__main__":
    # config_path = "chemin/vers/ta/config.txt"
    # print(extract_config_features(config_path))
    
    # Pour traiter un dossier entier:
    parse_folder_to_csv("/Users/chiba/Desktop/TB/configExtract/src/data/config/exemples_training_configs", "dataset.csv")