from abc import abstractmethod,ABC
from models import Interface


class Device(ABC):

    
    def __init__(self, macAdresse: str, hostname: str):
        self.macAdresse: str = macAdresse
        self.hostname: str = hostname
        self.interfaces: list = [Interface]

    def add_interface(self, interface: Interface):
        self.interfaces.append(interface)

    @abstractmethod
    def connect(self,a,b):
        """Méthode abstraite à implémenter dans les sous-classes"""
        pass

