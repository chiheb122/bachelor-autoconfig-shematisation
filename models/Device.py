import uuid
from abc import abstractmethod,ABC
from models import Interface


class Device(ABC):

    
    def __init__(self, macAdresse: str, hostname: str):
        self.macAdresse: str = macAdresse
        self.hostname: str = hostname
        self.ref_id: str = f"save-ref-id:{uuid.uuid4().int >> 64}"
        self.mem_addr: int = uuid.uuid4().int >> 52
        self.interfaces: list = []

    def add_interface(self, interface: Interface):
        # Ajoute un identifiant mémoire unique à chaque interface
        if not hasattr(interface, "mem_addr"):
            interface.mem_addr = uuid.uuid4().int >> 52
        self.interfaces.append(interface)

    @abstractmethod
    def connect(self,a,b):
        """Méthode abstraite à implémenter dans les sous-classes"""
        pass

