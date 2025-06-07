from models.Device import Device
import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)


class Router(Device):

    def __init__(self, macAdresse: str, hostname: str):
        super().__init__(macAdresse, hostname)
        self.router_template = None  # Initialisation


    def connect(self,a,b):
        pass

    # But : Charger le modèle de routeur (fichier XML contenant un seul <DEVICE>)
    def load_router(self):
        root = ET.parse("resources/xml/router.xml").getroot()
        self.router_template = root
        return root
    
    # ─────────────────────────────────────────────────────────────────────
    # Fonction : parseXml
    # But : Injecter un nouveau routeur dans le modèle
    # Arguments :
    #   - router_template : le modèle de routeur chargé depuis router.xml
    #   - hostname : nom à donner au routeur  
    def parseXml(self):
        if self.router_template is None:
            raise ValueError("Le modèle de routeur n'est pas chargé. Appelle load_router() echoue.")
        router = copy.deepcopy(self.router_template)  # On duplique le modèle pour pouvoir le modifier
        # Modifier le nom du routeur
        router.find(".//NAME").text = self.hostname
        # Modifier la position (décalage de +10 sur X, par exemple)
        logical = router.find(".//LOGICAL")
        if logical is not None:
            x_node = logical.find("X")
            y_node = logical.find("Y")
            if x_node is not None and x_node.text.isdigit():
                x_node.text = str(int(x_node.text) + 10)
            if y_node is not None and y_node.text.isdigit():
                y_node.text = str(int(y_node.text) + 10)
        return router
