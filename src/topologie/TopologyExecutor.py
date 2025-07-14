# src/topologie/topology_executor.py
from src.topologie.packet_tracer.PktBuilder import PktBuilder

class TopologyExecutor:
    @staticmethod
    def generate(devices,links, output_path="src/resources/generated/generated1.xml", notes=None, output_file="topologie_packet_tracer"):
        """
        """
        builder = PktBuilder(base_template_path="src/resources/xml/empty.xml", devices=devices,links=links, notes=notes)
        tree = builder.inject_devices()
        builder.generateXML(tree, output_path=f"{output_path}/{output_file}.xml")
        builder.generatePKT(xml_path=f"{output_path}/generated1.xml", output_path=f"{output_path}/{output_file}.pkt")
        print("✅ Fichier XML généré avec succès.")
