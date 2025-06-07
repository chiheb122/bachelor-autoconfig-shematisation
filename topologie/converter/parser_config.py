import re
from models.Interface import Interface

def detect_device_type(config_lines):
    for line in config_lines:
        if "hostname" in line:
            continue
        if line.startswith("interface Vlan") or "vlan" in line.lower():
            return "switch"
        if "router ospf" in line or "ip route" in line:
            return "router"
    return "unknown"

def parse_config_to_json(config_path):
    with open(config_path, "r") as f:
        lines = f.readlines()
    device_type = detect_device_type(lines)
    hostname = None
    interfaces = []
    current_intf = None
    ip_address = ""
    subnet_mask = ""
    status = "down"
    vlan = 1

    for line in lines:
        line = line.strip()
        if line.startswith("hostname"):
            hostname = line.split()[1].strip()
        elif line.startswith("interface"):
            if current_intf:
                interfaces.append(
                    Interface(
                        name=current_intf,
                        ip_address=ip_address,
                        subnet_mask=subnet_mask,
                        status=status,
                        vlan=vlan
                    )
                )
            current_intf = line.split()[1]
            ip_address = ""
            subnet_mask = ""
            status = "down"
            vlan = 1
        elif line.startswith("ip address") and current_intf:
            parts = line.split()
            if len(parts) >= 3:
                ip_address = parts[2]
                subnet_mask = parts[3] if len(parts) > 3 else ""
        elif "shutdown" in line and current_intf:
            status = "down"
        elif "no shutdown" in line and current_intf:
            status = "up"
        elif "switchport access vlan" in line and current_intf:
            vlan = int(line.split()[-1])
    # Ajouter la dernière interface si présente
    if current_intf:
        interfaces.append(
            Interface(
                name=current_intf,
                ip_address=ip_address,
                subnet_mask=subnet_mask,
                status=status,
                vlan=vlan
            )
        )

    config = {
        "raw": lines,
        "interfaces": interfaces
    }
    return {
        "type": device_type,
        "name": hostname or "Unknown",
        "mac": "00:11:22:33:44:55",
        "config": config
    }

def parse_cdp_neighbors(output):
    with open(output, "r") as f:
        lines = f.readlines()
        
    neighbors = []
    # Ignore header lines
    for line in lines[1:]:
        match = re.match(r"(\S+)\s+(\S+\s+\S+)\s+\d+\s+\S+\s+\S+\s+(\S+\s+\S+)", line)
        if match:
            device_id = match.group(1)
            local_intf = match.group(2).replace(" ", "")
            port_id = match.group(3).replace(" ", "")
            neighbors.append({
                "device_id": device_id,
                "local_interface": local_intf,
                "port_id": port_id
            })
    return neighbors