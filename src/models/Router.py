from ..models.Device import Device
import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)


class Router(Device):

    def __init__(self, macAdresse: str, hostname: str, config=None):
        super().__init__(macAdresse, hostname)
        self.router_template = None  # Initialisation
        self.config = config

    def connect(self, a, b):
        pass

    # But : Charger le modèle de routeur (fichier XML contenant un seul <DEVICE>)
    def load_router(self):
        root = ET.parse("src/resources/xml/router.xml").getroot()
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
        router.find(".//SYS_NAME").text = self.hostname

        # Injecter les identifiants uniques
        ref_id_node = router.find(".//SAVE_REF_ID")
        if ref_id_node is not None:
            ref_id_node.text = str(self.ref_id)
        mem_addr_node = router.find(".//MEM_ADDR")
        if mem_addr_node is not None:
            mem_addr_node.text = str(self.mem_addr)

        # Injecter la configuration ligne par ligne
        if self.config:
            running_node = router.find(".//RUNNINGCONFIG")
            startup_node = router.find(".//STARTUPCONFIG")

            if running_node is not None:
                self._inject_config_lines(running_node, self.config)

            if startup_node is not None:
                self._inject_config_lines(startup_node, self.config)

        # Modifier la position (décalage de +10 sur X, par exemple)
        logical = router.find(".//LOGICAL")
        if logical is not None:
            x_node = logical.find("X")
            y_node = logical.find("Y")
            if x_node is not None and x_node.text.isdigit():
                x_node.text = str(int(x_node.text) + 10)
            if y_node is not None and y_node.text.isdigit():
                y_node.text = str(int(y_node.text) + 10)

        # (Optionnel) Injecter les identifiants sur les interfaces
        # for intf in self.interfaces:
        #     intf_node = router.find(f".//INTERFACE[NAME='{intf.name}']")
        #     if intf_node is not None:
        #         mem_addr_node = intf_node.find("MEM_ADDR")
        #         if mem_addr_node is not None:
        #             mem_addr_node.text = str(intf.mem_addr)
        print(router)
        return router
