import uuid
from abc import abstractmethod,ABC
from ..models import Interface


class Device(ABC):

    
    def __init__(self, macAdresse: str, hostname: str):
        """
        Initialise une nouvelle instance de la classe Device.

        Args:
            macAdresse (str): L'adresse MAC de l'appareil.
            hostname (str): Le nom d'hôte de l'appareil.

        Attributs:
            macAdresse (str): L'adresse MAC de l'appareil.
            hostname (str): Le nom d'hôte de l'appareil.
            ref_id (str): Identifiant de référence généré de manière unique.
            mem_addr (int): Adresse mémoire générée de manière unique.
            interfaces (list): Liste des interfaces associées à l'appareil.
        """
        self.macAdresse: str = macAdresse
        self.hostname: str = hostname
        self.ref_id: str = f"save-ref-id:{uuid.uuid4().int >> 64}"
        self.mem_addr: int = uuid.uuid4().int >> 52
        self.interfaces: list = []

    def add_interface(self, interface: Interface):
        """
        Ajoute une interface à la liste des interfaces de l'appareil.

        Si l'interface ne possède pas déjà un identifiant mémoire unique (`mem_addr`), 
        un nouvel identifiant est généré à l'aide de uuid4 et assigné à l'attribut `mem_addr` de l'interface.

        Args:
            interface (Interface): L'interface à ajouter à l'appareil.
        """
        # Ajoute un identifiant mémoire unique à chaque interface
        if not hasattr(interface, "mem_addr"):
            interface.mem_addr = uuid.uuid4().int >> 52
        self.interfaces.append(interface)

    @abstractmethod
    def connect(self,a,b):
        """Méthode abstraite à implémenter dans les sous-classes"""
        pass

