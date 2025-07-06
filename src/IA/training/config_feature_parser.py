import re
import os
import pandas as pd

def is_config_ok(features):
    required_common = ["has_hostname", "has_enable_secret", "has_line_vty", "vty_has_login", "has_ssh"]
    routing_ok = features.get("Has_routing_protocole", 0)
    ospf_ok = not features.get("has_ospf", 0) or not features.get("ospf_no_network", 0)
    eigrp_ok = not features.get("has_eigrp", 0) or not features.get("eigrp_bad_network", 0)

    if all(features.get(k, 0) for k in required_common) and routing_ok and ospf_ok and eigrp_ok:
        return "ok"
    return "incomplete_config"

def extract_config_features(config_path):
    with open(config_path, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip() != ""]

    features = {
        "filename": os.path.basename(config_path),
        "has_hostname": 0,
        "has_secretPass": 0,
        "has_dhcp_server": 0,
        "ip_addresses_overlap": 0,
        "has_nat_configured": 0,
        "vtp_password_configured": 0,
        "Has_routing_protocole": 0,
        "has_description_on_interfaces": 0,
        "dhcp_pool_configured": 0,
        "has_cdp_enabled": 0,
        "no_ip_domain_lookup": 0,
        "has_ssh": 0,
        "vtp_domain_configured": 0,
        "vtp_mode": "none",
        "has_vlan": 0,
        "missing_network_on_routing": 0,
        "acl_configured": 0,
        "has_switchportonVlan": 0,
        "vlan_interface_management_ip": 0,
        "label": ""
    }

    interfaces = {}
    current_iface = None
    ip_map = set()

    for line in lines:
        l = line.lower()

        if l.startswith("hostname") and "router" not in l and "switch" not in l:
            features["has_hostname"] = 1

        if "enable secret" in l:
            features["has_secretPass"] = 1

        if l.startswith("ip dhcp pool"):
            features["dhcp_pool_configured"] = 1

        if l.startswith("ip dhcp") or "dhcp" in l:
            features["has_dhcp_server"] = 1

        if l.startswith("router ospf") or l.startswith("router rip") or l.startswith("router eigrp"):
            features["Has_routing_protocole"] = 1

        if l.startswith("interface"):
            current_iface = l.split()[1]
            interfaces[current_iface] = {}

        if current_iface:
            if "description" in l:
                features["has_description_on_interfaces"] = 1
            if "ip address" in l:
                try:
                    ip = l.split()[2]
                    if ip in ip_map:
                        features["ip_addresses_overlap"] = 1
                    else:
                        ip_map.add(ip)
                    if current_iface.startswith("vlan"):
                        features["vlan_interface_management_ip"] = 1
                except:
                    pass
            if "switchport access vlan" in l:
                features["has_switchportonVlan"] = 1

        if l.startswith("ip nat inside") or l.startswith("ip nat outside") or "overload" in l:
            features["has_nat_configured"] = 1

        if l.startswith("vtp password"):
            features["vtp_password_configured"] = 1

        if l.startswith("vtp domain"):
            features["vtp_domain_configured"] = 1

        if l.startswith("vtp mode"):
            try:
                features["vtp_mode"] = l.split()[2]
            except:
                pass

        if l.startswith("vlan") and "vlan" in l:
            features["has_vlan"] = 1

        if l.startswith("network") and ("ospf" in lines or "eigrp" in lines or "rip" in lines):
            features["missing_network_on_routing"] = 0
        elif any(proto in " ".join(lines) for proto in ["router ospf", "router eigrp", "router rip"]):
            features["missing_network_on_routing"] = 1

        if l.startswith("access-list") or "access-group" in l:
            features["acl_configured"] = 1

        if "cdp run" in l or "cdp enable" in l:
            features["has_cdp_enabled"] = 1

        if l.startswith("no ip domain-lookup"):
            features["no_ip_domain_lookup"] = 1

        if "crypto key" in l or "ip ssh" in l:
            features["has_ssh"] = 1

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
    lines = config_text.splitlines()
    result = []
    skip = False

    for line in lines:
        if any(kw in line for kw in block_keywords):
            skip = True
            continue
        if skip and (
                line.strip() == "!" or re.match(r"^(interface|router|line|end|hostname|access-list|!)", line.strip())):
            skip = False
        if not skip:
            result.append(line)

    return "\n".join(result)

if __name__ == "__main__":
    # folder_path = "D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/data/config/other"
    # output_csv = "dataset1.csv"
    # parse_folder_to_csv(folder_path, output_csv)
    print(extract_config_features("/Users/chiba/Desktop/TB/configExtract/src/IA/training/Router0_running-config.txt"))