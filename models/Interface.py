from dataclasses import dataclass

@dataclass
class Interface:
    name: str
    ip_address: str
    subnet_mask: str
    status: str
    vlan: int
