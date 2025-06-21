from src.models.Link import Link
from src.models.Switch import Switch
from src.models.Device import Device
from src.models.Router import Router
import xml.etree.ElementTree as ET
import sys
sys.path.append("lib/pka2xml_py")
import pka2core #type: ignore
from src.topologie.converter.pkt2xml import encrypt_xml_to_pkt  # Librairie standard pour manipuler du XML en Python


class PktBuilder:

    def __init__(self,base_template_path:str,devices:list[Device], links:list[Link] = None): # type: ignore
        self.base_template:str = base_template_path
        self.devices:devices[Device] = devices # type: ignore
        self.links = links if links is not None else []

    # Fonction : load_base
    # But : Charger le fichier de base (2.xml), qui ne contient que la structure du fichier .pkt sans DEVICE
    def load_base(self):
        tree = ET.parse("src/resources/xml/empty.xml")
        root = tree.getroot()
        return tree, root  # On retourne à la fois l'arbre complet (pour l'enregistrement) et la racine (pour injection)


    def inject_devices(self):
        """
        Injecte les appareils (routeurs, switches) et les liens dans la structure XML de base du fichier pkt.
        Cette méthode charge la structure de base du fichier pkt, puis ajoute les objets appareils (instances de Router ou Switch)
        dans le bloc <DEVICES> du document XML. Elle ajoute également les liens (instances de Link) dans le bloc <LINKS>.
        Si les blocs <DEVICES> ou <LINKS> sont absents dans la base XML, une exception est levée.
        Retourne :
            tree (ElementTree) : L'arbre XML modifié, prêt à être sauvegardé.
        Exceptions :
            ValueError : Si le bloc <DEVICES> ou <LINKS> est introuvable dans la base XML.
        Remarques :
            - Les types d'appareils non pris en charge sont signalés par un message d'avertissement.
            - Les types de liens non pris en charge sont également signalés par un message d'avertissement.
        """
        # Charger la structure de base du fichier pkt (sans appareils)
        tree, root = self.load_base()
        devices_node = root.find(".//DEVICES")
        if devices_node is None:
            raise ValueError("❌ Aucun bloc <DEVICES> trouvé dans la base XML")
        for device in self.devices:
            if isinstance(device, Router):
                # Ajouter le routeur modifié à la racine du document
                router_xml = device.parseXml()
                devices_node.append(router_xml)
            elif isinstance(device, Switch):
                # Ajouter le routeur modifié à la racine du document
                switch_xml = device.parseXml()
                devices_node.append(switch_xml)
            else:
                print(f"⚠️ Type d'appareil non pris en charge : {type(device)}")
        # Ajouter les liens
        for link in self.links:
            if isinstance(link, Link):
                # Ajouter le lien au bloc <LINKS>
                links_node = root.find(".//LINKS")
                if links_node is None:
                    raise ValueError("❌ Aucun bloc <LINKS> trouvé dans la base XML")
                link_xml = link.to_xml()
                links_node.append(link_xml)
            else:
                print(f"⚠️ Type de lien non pris en charge : {type(link)}")
     
        return tree  # Pour éventuellement sauvegarder ensuite via tree.write(...)
    

    def generateXML(self,tree, output_path="src/resources/generated/generated1.xml"):
        """
        Écrit l'arbre XML complet dans un fichier.
        """
        # for elem in tree.getroot().iter():
        #     if isinstance(elem.text, dict):
        #         print(f"❌ ERREUR: dict trouvé dans .text pour <{elem.tag}> : {elem.text}")
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"✅ Fichier généré avec succès : {output_path}")

    def generatePKT(self, xml_path: str, output_path="src/resources/generated/generated.pkt"):
        """
        Génère un fichier .pkt à partir d'un fichier XML spécifié.

        Cette méthode chiffre le fichier XML donné via le chemin `xml_path` en utilisant la fonction
        `encrypt_xml_to_pkt`, puis écrit le résultat chiffré dans un fichier de sortie au format binaire.
        Le chemin du fichier de sortie peut être spécifié via `output_path`, sinon il sera nommé
        "generated.pkt" par défaut.

        Args:
            xml_path (str): Chemin vers le fichier XML à chiffrer.
            output_path (str, optional): Chemin du fichier .pkt généré. Par défaut "generated.pkt".

        Raises:
            Exception: Affiche un message d'erreur si le chiffrement ou l'écriture échoue.

        Affiche:
            Un message de succès si le fichier est généré avec succès, sinon un message d'erreur.
        """
        try:
            pkt_bytes = encrypt_xml_to_pkt(xml_path)
            with open(output_path, "wb") as f:
                f.write(pkt_bytes)
            print(f"✅ Fichier .pkt généré avec succès : {output_path}")
        except Exception as e:
            print(f"❌ Erreur lors du chiffrement du fichier XML : {e}")


