# src/topologie/topology_builder.py
import re
from src.models.factory.DeviceFactory import DeviceFactory
from src.models.Link import Link

class TopologyBuilder:
    @staticmethod
    def create_devices(parsed_devices):
        devices = []
        for pd in parsed_devices:
            device = DeviceFactory.create_device(pd["type"], pd["mac"], pd["name"], pd["raw"])
            for intf in pd["config"]["interfaces"].values():
                device.add_interface(intf)
            device.load_router() if pd["type"] == "router" else device.load_switch()
            devices.append(device)
        return devices

    @staticmethod
    def build_links(devices, neighbors):
        seen = set()
        links = []

        devices_by_hostname = {d.hostname: d for d in devices}

        def is_vlan_subinterface(interface):
            return bool(re.search(r'/\d+\.\d+$', interface))

        for entry in neighbors:
            local_host = entry["device_id"]
            local_intf = entry["local_interface"]
            remote_intf = entry["port_id"]

            if is_vlan_subinterface(local_intf) or is_vlan_subinterface(remote_intf):
                continue

            dev_a = devices_by_hostname.get(local_host)
            dev_b = next(
                (d for d in devices if d != dev_a and any(intf.name.lower() == remote_intf.lower() for intf in d.interfaces)),
                None
            )


            if not dev_a or not dev_b:
                print(f"⚠️ Appareils introuvables pour {local_host} -> {remote_intf}")
                continue

            key = tuple(sorted([(dev_a.hostname, local_intf), (dev_b.hostname, remote_intf)]))
            if key in seen:
                continue

            seen.add(key)
            # tester si les appareils sont de meme type 
            if type(dev_a) == type(dev_b):
                cable_type = "eCrossOver"
            else:
                cable_type = "eStraight"
            
            links.append(Link(dev_a, local_intf, dev_b, remote_intf, cable_type=cable_type))

        return links
