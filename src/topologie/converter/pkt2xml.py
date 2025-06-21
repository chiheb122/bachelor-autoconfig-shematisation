from pathlib import Path
import re
import pka2core #type: ignore

def decrypt_pkt_to_xml(input_path: str) -> str:
    """
    Déchiffre un fichier .pkt ou .pka et retourne le contenu XML en chaîne de caractères.
    """
    input_path = Path(input_path)
    with open(input_path, "rb") as f:
        data = f.read()
    xml_str = pka2core.decrypt_pka(data)
    return xml_str


def encrypt_xml_to_pkt(xml_path: str, fix_version: bool = True) -> bytes:
    """
    Chiffre un fichier XML en binaire .pkt.
    Si `fix_version` est True, remplace la balise <VERSION> pour compatibilité Packet Tracer.
    """
    xml_path = Path(xml_path)
    with open(xml_path, "r", encoding="utf-8") as f:
        xml = f.read()

    if fix_version:
        xml = re.sub(r"<VERSION>.*?</VERSION>", "<VERSION>8.2.2.0400</VERSION>", xml)

    xml_bytes = xml.encode("utf-8")
    pkt_bytes = pka2core.encrypt_pka(xml_bytes)
    return pkt_bytes


if __name__ == "__main__":
    xml_text = decrypt_pkt_to_xml("/Users/chiba/Desktop/TB/configExtract/resources/pkt/empty.pkt")
    # Décryptage
    input_file = Path("/Users/chiba/Desktop/TB/configExtract/resources/pkt/empty.pkt")
    # Création du chemin de sortie avec extension .xml
    output_file = input_file.with_suffix(".xml")

    # Sauvegarde du fichier XML
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(xml_text)

    print(f"✅ XML sauvegardé dans : {output_file}")

