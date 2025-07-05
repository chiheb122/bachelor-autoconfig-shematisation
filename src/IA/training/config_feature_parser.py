import re
import os
import pandas as pd
import re
def is_config_ok(features):
    # Critères communs à tous les équipements
    required_common = ["has_hostname", "has_enable_secret", "has_line_vty", "vty_has_login", "has_ssh"]

    # Cas routeur : besoin d’un moyen de routage
    routing_ok = (
        features["has_ospf"] or features["has_rip"] or features["has_eigrp"] or features["has_static"]
    )

    # Si OSPF ou EIGRP sont présents, leurs networks doivent être définis
    ospf_ok = not features["has_ospf"] or (features["has_ospf"] and not features["ospf_no_network"])
    eigrp_ok = not features["has_eigrp"] or (features["has_eigrp"] and not features["eigrp_bad_network"])

    # Aucune erreur critique
    if all(features.get(k, 0) for k in required_common) and routing_ok and ospf_ok and eigrp_ok:
        return "ok"
    return "incomplete_config"

def extract_config_features(config_path):
    with open(config_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != ""]

    features = {
        "filename": os.path.basename(config_path),
        "device_type": "router",
        "has_ospf": 0,
        "has_rip": 0,
        "has_eigrp": 0,
        "has_static": 0,
        "nb_interfaces": 0,
        "nb_subinterfaces": 0,
        "ospf_no_network": 0,
        "eigrp_bad_network": 0,
        "missing_redis_static": 0,
        "uses_vlan": 0,
        "has_switchport": 0,
        "has_enable_secret": 0,
        "has_line_vty": 0,
        "vty_has_login": 0,
        "vty_has_transport_input": 0,
        "has_ssh": 0,
        "has_password_plaintext": 0,
        "has_hostname": 0,
        "has_acl": 0,
        "has_vtp": 0,
        "has_trunk": 0,
        "has_access_ports": 0,
        "label": ""
    }

    in_router_block = None
    in_vty_block = False
    in_interface_block = False
    router_blocks = {"ospf": [], "rip": [], "eigrp": []}
    interface_count = 0
    subinterface_count = 0
    has_static_routes = False
    static_found = False
    networks_found = {"ospf": False, "eigrp": False}

    for i, line in enumerate(lines):
        if line.startswith("interface"):
            interface_count += 1
            in_interface_block = True
            if "." in line:
                subinterface_count += 1
            continue

        if in_interface_block and (line.startswith("!") or line.startswith("interface")):
            in_interface_block = False

        if in_interface_block:
            if "switchport mode trunk" in line:
                features["has_trunk"] = 1
            if "switchport mode access" in line:
                features["has_access_ports"] = 1

        if line.startswith("ip route"):
            has_static_routes = True

        if "switchport" in line:
            features["has_switchport"] = 1

        if line.startswith("interface vlan"):
            features["uses_vlan"] = 1

        if line.startswith("vtp mode") or line.startswith("vtp domain"):
            features["has_vtp"] = 1

        if line.startswith("enable secret"):
            features["has_enable_secret"] = 1

        if line.startswith("line vty"):
            features["has_line_vty"] = 1
            in_vty_block = True
            continue

        if in_vty_block:
            if line.startswith("!") or line.startswith("line"):
                in_vty_block = False
            else:
                if "login" in line:
                    features["vty_has_login"] = 1
                if "transport input" in line:
                    features["vty_has_transport_input"] = 1

        if "ip ssh" in line or "crypto key generate rsa" in line:
            features["has_ssh"] = 1

        if re.match(r"password \d? \S+", line):
            features["has_password_plaintext"] = 1

        if line.startswith("hostname"):
            features["has_hostname"] = 1

        if line.startswith("access-list") or "ip access-group" in line:
            features["has_acl"] = 1

        if line.startswith("router ospf"):
            features["has_ospf"] = 1
            in_router_block = "ospf"
            continue

        if line.startswith("router rip"):
            features["has_rip"] = 1
            in_router_block = "rip"
            continue

        if line.startswith("router eigrp"):
            features["has_eigrp"] = 1
            in_router_block = "eigrp"
            continue

        if line.startswith("router"):
            in_router_block = None

        if in_router_block:
            router_blocks[in_router_block].append(line)
            if line.strip().startswith("network"):
                networks_found[in_router_block] = True
            if in_router_block == "eigrp" and "redistribute static" in line:
                static_found = True

    features["nb_interfaces"] = interface_count
    features["nb_subinterfaces"] = subinterface_count
    features["has_static"] = 1 if has_static_routes else 0
    features["missing_redis_static"] = 1 if has_static_routes and not static_found else 0
    features["ospf_no_network"] = 1 if features["has_ospf"] and not networks_found["ospf"] else 0
    features["eigrp_bad_network"] = 1 if features["has_eigrp"] and not networks_found["eigrp"] else 0

    if features["has_switchport"] or features["uses_vlan"]:
        features["device_type"] = "switch"

    features["label"] = is_config_ok(features)

    return features

def parse_folder_to_csv(folder_path, output_csv="dataset.csv"):
    data = []
    for file in os.listdir(folder_path):
        if file.endswith(".txt") and "config" in file:
            full_path = os.path.join(folder_path, file)
            features = extract_config_features(full_path)
            data.append(features)

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"✅ Dataset enregistré dans {output_csv}")
    return df


def generate_variant(config_text: str, block_keywords: list[str]) -> str:
    """
    Supprime les blocs de configuration contenant certains mots-clés.

    Args:
        config_text (str): Le contenu brut de la configuration.
        block_keywords (list[str]): Liste de mots-clés à rechercher pour supprimer les blocs associés.

    Returns:
        str: La configuration modifiée avec les blocs supprimés.
    """
    lines = config_text.splitlines()
    result = []
    skip = False

    for line in lines:
        # Si le début d'un bloc contient un mot-clé
        if any(kw in line for kw in block_keywords):
            skip = True
            continue
        # Si on arrive à un nouveau bloc, on arrête de sauter
        if skip and (
                line.strip() == "!" or re.match(r"^(interface|router|line|end|hostname|access-list|!)", line.strip())):
            skip = False
        if not skip:
            result.append(line)

    return "\n".join(result)


if __name__ == "__main__":
    folder_path = "D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/data/config/train"
    output_csv = "dataset.csv"
    parse_folder_to_csv(folder_path, output_csv)

    #with open("D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/config/save/base_switch.txt", "r") as f:
    #    config = f.read()
    #variant = generate_variant(config, ["hostname"])

    #with open("../../data/config/train/variant_ok_SW_config.txt", "w") as f:
    #    f.write(variant)



