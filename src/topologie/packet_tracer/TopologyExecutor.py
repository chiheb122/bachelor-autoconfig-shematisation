# src/topologie/topology_executor.py
from src.topologie.packet_tracer.draw.PktBuilder import PktBuilder

class TopologyExecutor:
    @staticmethod
    def generate(devices,links, output_path="src/resources/generated/generated1.xml", notes=None):
        """
        """
        builder = PktBuilder(base_template_path="src/resources/xml/empty.xml", devices=devices,links=links, notes=notes)
        tree = builder.inject_devices()
        builder.generateXML(tree)
        builder.generatePKT(output_path)
        print("✅ Fichier XML généré avec succès.")
