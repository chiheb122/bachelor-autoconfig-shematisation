from pathlib import Path
#from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama.llms import OllamaLLM
from langchain_groq import ChatGroq
from src.topologie.packet_tracer.TopologyLoader import TopologyLoader


class ConfigAnalyzerAgent:
    def __init__(self):

        #self.llm = OllamaLLM(model="mistral:latest", temperature=0.1, max_tokens=1000)

        self.llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            temperature=0,
            max_tokens=None,
            reasoning_format="parsed",
            timeout=None,
            max_retries=2,
            api_key="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"
        )
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
        # Générer le message à partir du prompt
        messages = self.prompt.invoke({"configs": configs})
        # Appeler le LLM avec les messages générés
        response = self.llm.invoke(messages)
        # Retourner le contenu du résultat
        return response.content if hasattr(response, "content") else response

    def returnConfigs(self,devices):
        # Générer une liste qui contient seulement les configs
        configs = []
        for device in devices :
            config = device["raw"]
            configs.append(config)

        return configs




if __name__ == '__main__':
    folder = input("Entrez le chemin du dossier de configs : ").strip()
    folder = folder if folder else "D:/HEG/sem6/TB/Tb_code/bachelor-autoconfig-shematisation/src/data/configs/packet"
    parsed_devices, neighbors = TopologyLoader.load_config_from_folder(folder)

    # # Appeler l'agent expert
    agent = ConfigAnalyzerAgent()
    configs = agent.returnConfigs(parsed_devices)
    response = agent.analyze_configs(configs)
    # Afficher le résultat de l'analyse
    print("\n Résultat de l'analyse expert réseau:\n")
    print(response)