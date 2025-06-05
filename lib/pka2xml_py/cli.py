import argparse
from pathlib import Path
import pka2core  # Le module compilé natif .so
import re

def main():
    parser = argparse.ArgumentParser(description="Convert .pkt/.pka files to/from XML using Packet Tracer logic.")
    parser.add_argument("mode", choices=["decrypt", "encrypt"], help="Mode: decrypt or encrypt")
    parser.add_argument("input", help="Input file path (.pkt, .pka or .xml)")
    parser.add_argument("output", help="Output file path")

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if args.mode == "decrypt":
        print(f"🔓 Décryptage de {input_path} vers {output_path}...")
        with open(input_path, "rb") as f:
            data = f.read()
        result = pka2core.decrypt_pka(data)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print("✅ Décryptage terminé !")

    elif args.mode == "encrypt":
        print(f"🔐 Chiffrement de {input_path} vers {output_path}...")
        with open(input_path, "r", encoding="utf-8") as f:
            xml = f.read()
        # 🔁 Forcer la version pour compatibilité maximale
        xml = re.sub(r"<VERSION>.*?</VERSION>", "<VERSION>8.2.2.0400</VERSION>", xml)        # 🔒 On encode en UTF-8 pour que encrypt_pka reçoive des bytes
        xml_bytes = xml.encode("utf-8")
        result = pka2core.encrypt_pka(xml_bytes)
        
        with open(output_path, "wb") as f:
            f.write(result)
        print("✅ Chiffrement terminé !")

if __name__ == "__main__":
    main()
