from ..models.Device import Device
import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)


class Switch(Device):
    position_offset = 0  # Compteur de classe partagé par tous les objets Switch

    """
    Initialise une nouvelle instance de la classe Switch.
    """
    def __init__(self, macAdresse: str, hostname: str, config=None, notconfigured: bool = False):
        super().__init__(macAdresse, hostname)
        self.switch_template = None  # Initialisation
        self.config = config
        self.position_x = 0
        self.position_y = 0

    def connect(self, a, b):
        pass

    # But : Charger le modèle de switcher (fichier XML contenant un seul <DEVICE>)
    def load_switch(self):
        root = ET.parse("src/resources/xml/switch.xml").getroot()
        self.switch_template = root
        return root

        """
        Analyse et modifie un modèle XML de switch en injectant des valeurs spécifiques à l'instance.

        Cette méthode duplique le modèle de switch XML, puis :
        - Modifie le nom du switch avec la valeur de `self.hostname`.
        - Injecte l'identifiant unique `self.ref_id` dans le noeud SAVE_REF_ID si présent.
        - Décale la position logique du switch de +10 sur les axes X et Y si ces valeurs existent et sont numériques.

        Retourne :
            ElementTree.Element: L'élément XML du switch modifié.

        Lève :
            ValueError: Si le modèle de switch (`self.switch_template`) n'est pas chargé.
        """

    def parseXml(self):
        if self.switch_template is None:
            raise ValueError("Le modèle de switch n'est pas chargé. Appelle load_switch() echoue.")
        switch = copy.deepcopy(self.switch_template)  # On duplique le modèle pour pouvoir le modifier
        # Modifier le nom du switcher
        switch.find(".//NAME").text = self.hostname
        switch.find(".//SYS_NAME").text = self.hostname
         # Injecter les identifiants uniques
        ref_id_node = switch.find(".//SAVE_REF_ID")
        if ref_id_node is not None:
            ref_id_node.text = str(self.ref_id)

        # Injecter la configuration ligne par ligne
        if self.config:
            running_node = switch.find(".//RUNNINGCONFIG")
            startup_node = switch.find(".//STARTUPCONFIG")

            if running_node is not None:
                self._inject_config_lines(running_node, self.config)

            if startup_node is not None:
                self._inject_config_lines(startup_node, self.config)

        # Modifier la position (décalage unique pour chaque switch)
        logical = switch.find(".//WORKSPACE//LOGICAL")
        if logical is not None:
            x_node = logical.find("X")
            y_node = logical.find("Y")
            if x_node is not None and x_node.text.isdigit():
                self.position_x = int(float(x_node.text)) + 50 * Switch.position_offset
                x_node.text = str(self.position_x)
            if y_node is not None and y_node.text.isdigit():
                self.position_y = int(float(y_node.text)) + 50 * Switch.position_offset
                y_node.text = str(self.position_y)
            Switch.position_offset += 1  # Incrémente pour le prochain switch
        return switch


    """ Retourne la position du switch."""
    def get_position(self):
        return self.position_x, self.position_y

