# Exemple basique
import subprocess
from pathlib import Path

def decode(pkt_path: Path, output_xml: Path):
    subprocess.run(["./lib/pka2xml", "-d", str(pkt_path), str(output_xml)], check=True)

def encode(xml_path: Path, output_pkt: Path):
    subprocess.run(["./lib/pka2xml", "-e", str(xml_path), str(output_pkt)], check=True)
