from models.Device import Device
import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)


class Switch(Device):

    def __init__(self, macAdresse: str, hostname: str):
        super().__init__(macAdresse, hostname)
        self.switch_template = None  # Initialisation


    def connect(self,a,b):
        pass

    # But : Charger le modèle de switcher (fichier XML contenant un seul <DEVICE>)
    def load_switch(self):
        root = ET.parse("resources/xml/switch.xml").getroot()
        self.switch_template = root
        return root
    
    def parseXml(self):
        if self.switch_template is None:
            raise ValueError("Le modèle de switch n'est pas chargé. Appelle load_switch() echoue.")
        switch = copy.deepcopy(self.switch_template)  # On duplique le modèle pour pouvoir le modifier
        # Modifier le nom du switcher
        switch.find(".//NAME").text = self.hostname
        # Modifier la position (décalage de +10 sur X, par exemple)
        logical = switch.find(".//LOGICAL")
        if logical is not None:
            x_node = logical.find("X")
            y_node = logical.find("Y")
            if x_node is not None and x_node.text.isdigit():
                x_node.text = str(int(x_node.text) + 10)
            if y_node is not None and y_node.text.isdigit():
                y_node.text = str(int(y_node.text) + 10)
        return switch
