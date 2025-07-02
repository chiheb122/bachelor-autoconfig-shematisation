from ..models.Device import Device
import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)


class Switch(Device):
    position_offset = 0  # Compteur de classe partagé par tous les objets Switch

    def __init__(self, macAdresse: str, hostname: str, config=None):
        """
        Initialise une nouvelle instance de la classe Switch.

        Args:
            macAdresse (str): L'adresse MAC du switch.
            hostname (str): Le nom d'hôte du switch.
            config (optionnel): La configuration initiale du switch. Par défaut à None.

        Attributs:
            switch_template: Modèle de configuration du switch, initialisé à None.
            config: Configuration du switch, peut être None ou un objet de configuration.
        """
        super().__init__(macAdresse, hostname)
        self.switch_template = None  # Initialisation
        self.config = config

    def connect(self, a, b):
        pass

    # But : Charger le modèle de switcher (fichier XML contenant un seul <DEVICE>)
    def load_switch(self):
        root = ET.parse("src/resources/xml/switch.xml").getroot()
        self.switch_template = root
        return root



    def parseXml(self):
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
                x_node.text = str(int(x_node.text) + 50 * Switch.position_offset)
            if y_node is not None and y_node.text.isdigit():
                y_node.text = str(int(y_node.text) + 50 * Switch.position_offset)
            Switch.position_offset += 1  # Incrémente pour le prochain switch
        return switch



