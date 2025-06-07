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
    
    def to_xml(self):
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
        <FROM_DEVICE_MEM_ADDR>{self.from_device_mem_addr}</FROM_DEVICE_MEM_ADDR>
        <TO_DEVICE_MEM_ADDR>{self.to_device_mem_addr}</TO_DEVICE_MEM_ADDR>
        <FROM_PORT_MEM_ADDR>{self.from_port_mem_addr}</FROM_PORT_MEM_ADDR>
        <TO_PORT_MEM_ADDR>{self.to_port_mem_addr}</TO_PORT_MEM_ADDR>
        <GEO_VIEW_COLOR>{self.color}</GEO_VIEW_COLOR>
        <IS_MANAGED_IN_RACK_VIEW>false</IS_MANAGED_IN_RACK_VIEW>
        <TYPE>{self.cable_type}</TYPE>
    </CABLE>
</LINK>
        """.strip()