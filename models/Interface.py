from dataclasses import dataclass
"""
Classe représentant une interface réseau.

Attributs :
    name (str) : Le nom de l'interface.
    ip_address (str) : L'adresse IP assignée à l'interface.
    subnet_mask (str) : Le masque de sous-réseau de l'interface.
    status (str) : L'état de l'interface (par exemple, 'up' ou 'down').
    vlan (int) : L'identifiant VLAN associé à l'interface.
"""
@dataclass
class Interface:
    name: str
    ip_address: str
    subnet_mask: str
    status: str
    vlan: int
