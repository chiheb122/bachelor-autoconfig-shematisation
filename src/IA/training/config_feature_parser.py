import re
import os
import pandas as pd

def extract_config_features(config_path):
    with open(config_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != ""]

    features = {
        "filename": os.path.basename(config_path),
        "device_type": "router",  # sera ajusté automatiquement
        "has_ospf": 0,
        "has_rip": 0,
        "has_eigrp": 0,
        "has_static": 0,
        "nb_interfaces": 0,
        "ospf_no_network": 0,
        "eigrp_bad_network": 0,
        "missing_redis_static": 0,
        "uses_vlan": 0,
        "has_switchport": 0,
        "label": ""
    }

    in_router_block = None
    router_blocks = {"ospf": [], "rip": [], "eigrp": []}
    interface_count = 0
    has_static_routes = False
    static_found = False
    networks_found = {"ospf": False, "eigrp": False}

    for line in lines:
        if line.startswith("interface"):
            interface_count += 1

        if line.startswith("ip route"):
            has_static_routes = True

        if "switchport" in line:
            features["has_switchport"] = 1

        if line.startswith("interface vlan"):
            features["uses_vlan"] = 1

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
    features["has_static"] = 1 if has_static_routes else 0
    features["missing_redis_static"] = 1 if has_static_routes and not static_found else 0
    features["ospf_no_network"] = 1 if features["has_ospf"] and not networks_found["ospf"] else 0
    features["eigrp_bad_network"] = 1 if features["has_eigrp"] and not networks_found["eigrp"] else 0

    # Déduire type de périphérique
    if features["has_switchport"] or features["uses_vlan"]:
        features["device_type"] = "switch"

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

if __name__ == "__main__":
    folder_path = "/Users/chiba/Desktop/TB/configExtract/src/data/config/reseau12"  # Remplacez par le chemin de votre dossier de configurations
    output_csv = "dataset.csv"
    parse_folder_to_csv(folder_path, output_csv)