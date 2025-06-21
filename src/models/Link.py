import xml.etree.ElementTree as ET  # Librairie standard pour manipuler du XML en Python
import copy  # Permet de dupliquer un objet (deepcopy pour dupliquer entièrement un arbre XML)



class Link:
    """
    Représente une connexion entre deux interfaces d'appareils réseau.
    """
    def __init__(self, device_a, iface_a, device_b, iface_b, link_type="eCopper", cable_type="eStraightThrough", length=1):
        self.device_a = device_a          # Instance d'appareil (ex: Router, Switch)
        self.iface_a = iface_a            # Nom de l'interface sur device_a (ex: "GigabitEthernet0/0")
        self.device_b = device_b
        self.iface_b = iface_b
        self.link_type = link_type        # eCopper, eFiber, etc.
        self.cable_type = cable_type      # eStraightThrough, eCrossOver, etc.
        self.length = length              # Longueur du câble (optionnel)
        link_template = None

    # But : Charger le modèle de link (fichier XML contenant un seul <Link>)
    def load_link(self):
        root = ET.parse("src/resources/xml/link.xml").getroot()
        self.link_template = root
        return root


    def to_dict(self):
        """
        Retourne une représentation dict pour la génération XML ou debug.
        """
        return {
            "device_a": self.device_a.name,
            "iface_a": self.iface_a,
            "device_b": self.device_b.name,
            "iface_b": self.iface_b,
            "link_type": self.link_type,
            "cable_type": self.cable_type,
            "length": self.length
        }
    
    def _get_port_mem_addr(self, device, iface_name):
        for intf in device.interfaces:
            if intf.name == iface_name:
                return getattr(intf, "mem_addr", "")
        return ""

    def to_xml_manuel(self):
        """
        Génère le XML <LINK> correspondant à ce lien.
        """
        return f"""
            <LINK>
                <TYPE>{self.link_type}</TYPE>
                <CABLE>
                    <LENGTH>{self.length}</LENGTH>
                    <FUNCTIONAL>true</FUNCTIONAL>
                    <FROM>{self.device_a.ref_id}</FROM>
                    <PORT>{self.iface_a}</PORT>
                    <TO>{self.device_b.ref_id}</TO>
                    <PORT>{self.iface_b}</PORT>
                    <FROM_DEVICE_MEM_ADDR>{self.device_a.mem_addr}</FROM_DEVICE_MEM_ADDR>
                    <TO_DEVICE_MEM_ADDR>{self.device_b.mem_addr}</TO_DEVICE_MEM_ADDR>
                    <FROM_PORT_MEM_ADDR>{self._get_port_mem_addr(self.device_a, self.iface_a)}</FROM_PORT_MEM_ADDR>
                    <TO_PORT_MEM_ADDR>{self._get_port_mem_addr(self.device_b, self.iface_b)}</TO_PORT_MEM_ADDR>
                    <GEO_VIEW_COLOR>{getattr(self, "color", "#6ba72e")}</GEO_VIEW_COLOR>
                    <IS_MANAGED_IN_RACK_VIEW>false</IS_MANAGED_IN_RACK_VIEW>
                    <TYPE>{self.cable_type}</TYPE>
                </CABLE>
            </LINK>
                    """.strip()


    def to_xml(self):
        """
        Génère le XML <LINK> correspondant à ce lien en utilisant le modèle chargé.
        """
        self.load_link()
        if self.link_template is None:
            raise ValueError("Le modèle de link n'est pas chargé. Appelle load_link() échoue.")
        
        link = copy.deepcopy(self.link_template)

        # Modifier le type de câble
        link.find(".//TYPE").text = self.link_type

        # Injecter les identifiants des devices
        link.find(".//FROM").text = self.device_a.ref_id
        link.find(".//TO").text = self.device_b.ref_id

        # Injecter les ports dans le bon ordre
        ports = link.findall(".//PORT")
        if len(ports) >= 2:
            ports[0].text = self.iface_b
            ports[1].text = self.iface_a
        else:
            raise ValueError("Le modèle de link ne contient pas deux balises <PORT>")

        return link

