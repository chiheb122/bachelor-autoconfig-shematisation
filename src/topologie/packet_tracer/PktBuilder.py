from src.models.Link import Link
from src.models.Switch import Switch
from src.models.Device import Device
from src.models.Router import Router
import xml.etree.ElementTree as ET
import sys
sys.path.append("lib/pka2xml_py")
from src.topologie.packet_tracer.pkt2xml import encrypt_xml_to_pkt ,decrypt_pkt_to_xml # Librairie standard pour manipuler du XML en Python
import copy

class PktBuilder:

    def __init__(self,base_template_path:str,devices:list[Device], links:list[Link] = None, notes:str = None): # type: ignore
        self.base_template:str = base_template_path
        self.devices:devices[Device] = devices # type: ignore
        self.links = links if links is not None else []
        self.notes = notes if notes is not None else "pas de notes"

    # Fonction : load_base
    # But : Charger le fichier de base (2.xml), qui ne contient que la structure du fichier .pkt sans DEVICE
    def load_base(self):
        tree = ET.parse("src/resources/xml/empty.xml")
        root = tree.getroot()
        return tree, root  # On retourne à la fois l'arbre complet (pour l'enregistrement) et la racine (pour injection)

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
    def inject_devices(self):
        # Charger la structure de base du fichier pkt (sans appareils)
        tree, root = self.load_base()
        devices_node = root.find(".//DEVICES")
        rectangles_to_add = []

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
            # Ajout des rectangles pour les appareils en cas de besoin
            if device.notconfigured:
                x, y = device.get_position()
                if x is not None and y is not None:
                    rectangles_to_add.append((x, y))

        rectangles_node = root.find("RECTANGLES")
        # Ajouter les rectangles pour les appareils non configurés
        if rectangles_to_add:
            for x, y in rectangles_to_add:
                rectangles_node.append(self.add_rectangle(x, y))  # Ajouter le rectangle à la liste des rectangles

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
        # Ajout des notes si elles existent
        physical_ws = root.find(".//PHYSICALWORKSPACE")
        if physical_ws is None:
            raise ValueError("Aucun bloc <PHYSICALWORKSPACE> trouvé dans la base XML")
        notes_node = physical_ws.find("NOTES")
        if notes_node is None:
            raise ValueError("Aucun bloc <NOTES> trouvé dans la base XML")
        else: 
            notes_node.append(self.add_note("src/resources/xml/note.xml", 49, 56, 40006, self.notes))  # Exemple d'ajout de note

        return tree  # Pour éventuellement sauvegarder ensuite via tree.write(...)
    
    """
        Écrit l'arbre XML complet dans un fichier.
    """
    def generateXML(self,tree, output_path="src/resources/generated/generated1.xml"):
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"✅ Fichier généré avec succès : {output_path}")

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
    def generatePKT(self, xml_path: str, output_path="src/resources/generated/generated.pkt"):
        try:
            pkt_bytes = encrypt_xml_to_pkt(xml_path)
            with open(output_path, "wb") as f:
                f.write(pkt_bytes)
            print(f"Fichier .pkt généré avec succès : {output_path}")
        except Exception as e:
            print(f"Erreur lors du chiffrement du fichier XML : {e}")


    def decryptPKT(self, pkt_path: str, output_xml_path="src/resources/generated/decryptedRc.xml"):
        """
        Déchiffre un fichier .pkt et enregistre le contenu XML dans un fichier. 
        """
        try:
            xml_content = decrypt_pkt_to_xml(pkt_path)
            with open(output_xml_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            print(f"Fichier XML déchiffré avec succès : {output_xml_path}")
        except Exception as e:
            print(f"Erreur lors du déchiffrement du fichier .pkt : {e}")

    """
    Une fonction pour ajouter des notes dans le fichier XML.
    Cette fonction prend en entrée un fichier XML, une position (x, y, z)
    et un texte pour la note, puis ajoute une note dans le fichier XML.
    """
    def add_note(self, xml_path: str, x: int, y: int, z: int, text: str):
        try:
            # Charger le modèle de note
            note_tree = ET.parse(xml_path)
            note_root = note_tree.getroot()
            note_copy = copy.deepcopy(note_root)  # Créer une copie de la note pour éviter de modifier le modèle original
            # Modifier les attributs de la note
            note_copy.find(".//X").text = str(x)
            note_copy.find(".//Y").text = str(y)
            note_copy.find(".//Z").text = str(z)
            note_copy.find(".//TEXT").text = text
    
            print(note_copy)
            return note_copy  # Retourne la note ajoutée pour une éventuelle utilisation ultérieure
        except ET.ParseError as e:
            print(f"Erreur de parsing XML : {e}")
        except Exception as e:
            print(f"Erreur lors de l'ajout de la note : {e}")

    """    Fonction pour ajouter un rectangle dans le fichier XML.
    """
    def add_rectangle(self, x: int, y: int):
        try:
            # Charger le modèle de rectangle
            rect_tree = ET.parse("src/resources/xml/rectangleRed.xml")
            rect_root = rect_tree.getroot()
            rect_copy = copy.deepcopy(rect_root)  # Créer une copie du rectangle pour éviter de modifier le modèle original

            # Modifier les attributs du rectangle
            offset = 30
            rect_copy.find("TopLeftX").text = str(x - offset)
            rect_copy.find("TopLeftY").text = str(y - offset)
            rect_copy.find("BottomRightX").text = str(x + offset)
            rect_copy.find("BottomRightY").text = str(y + offset)

            return rect_copy  # Retourne le rectangle ajouté pour une éventuelle utilisation ultérieure
        except ET.ParseError as e:
            print(f"Erreur de parsing XML : {e}")
        except Exception as e:
            print(f"Erreur lors de l'ajout du rectangle : {e}")

# if __name__ == "__main__":
#     pkt_builder = PktBuilder()
#     # Exemple d'utilisation des méthodes
#     pkt_builder.decryptPKT("/Users/chiba/Desktop/TB/configExtract/src/resources/generated/63-13_SimulationRC_65200.pkt")