def parse_config_to_json(config_path):
    router = {"hostname": None, "interfaces": []}
    current_iface = None

    with open(config_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("hostname"):
                router["hostname"] = line.split()[1]
            elif line.startswith("interface"):
                if current_iface:
                    router["interfaces"].append(current_iface)
                current_iface = {"name": line.split()[1], "ip": None, "status": "up"}
            elif line.startswith("ip address") and current_iface:
                parts = line.split()
                if len(parts) >= 4:
                    ip = parts[2]
                    mask = parts[3]
                    current_iface["ip"] = {"address": ip, "mask": mask}

            elif "shutdown" in line and current_iface:
                current_iface["status"] = "down"
        
        if current_iface:
            router["interfaces"].append(current_iface)
    
    return router
