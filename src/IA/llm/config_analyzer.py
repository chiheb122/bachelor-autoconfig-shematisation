from pathlib import Path
# from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader


class ConfigAnalyzerAgent:
    def __init__(self):
        self.llm = OllamaLLM(model="mistral:latest", temperature=0.1, max_tokens=1000)
        # Charger le prompt depuis le fichier
        template_path = Path(__file__).parent / "prompt_template.txt"
        system_template = template_path.read_text()
        # Créer le prompt template avec les nouveaux rôles
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template.replace('"statut"', 'statut')),  # Échappement des variables
                ("user", "{configs}"),
            ]
        )

    def analyze_configs(self, configs: str) -> str:
        # 2. Configuration de test
        config_test = """
            !
            version 15.2
            hostname R1
            !
            enable secret 5 $1$abC1$E3yK0nF0gQsL3i5aLx4pG.
            no ip domain-lookup
            !
            interface GigabitEthernet0/0
             ip address 192.168.1.1 255.255.255.0
             no shutdown
            !
            interface GigabitEthernet0/1
             ip address 10.0.0.1 255.255.255.0
             no shutdown
             description vers LAN
            !
            router ospf 1
             network 192.168.1.0 0.0.0.255 area 0
            !
            ip route 0.0.0.0 0.0.0.0 10.0.0.254
            !
            line vty 0 4
             login
             transport input ssh
            !
            crypto key generate rsa
            ip ssh version 2
            !
            access-list 10 permit 192.168.1.0 0.0.0.255
            !
            end
        """
        # Générer le message à partir du prompt
        messages = self.prompt.invoke({"configs": configs})
        # Appeler le LLM avec les messages générés
        response = self.llm.invoke(messages)
        # Retourner le contenu du résultat
        return response.content if hasattr(response, "content") else response

    def returnConfigs(self,devices):
        configs = []
        for device in devices :
            config = device["raw"]
            configs.append(config)

        return configs




if __name__ == '__main__':
    folder = input("Entrez le chemin du dossier de config : ").strip()
    folder = folder if folder else "D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/data/config/packet"
    parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)

    # # Appeler l'agent expert
    agent = ConfigAnalyzerAgent()
    configs = agent.returnConfigs(parsed_devices)
    response = agent.analyze_configs(configs)
    # Afficher le résultat de l'analyse
    print("\n Résultat de l'analyse expert réseau:\n")
    print(response)