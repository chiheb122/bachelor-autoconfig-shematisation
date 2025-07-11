from pathlib import Path
# from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


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
        hostname R1
        enable secret 9 $tr0ngP@ss
        interface GigabitEthernet0/0
        ip address 192.168.1.1 255.255.255.0
        line vty 0 4
        login local
        ! Manque SSH et ACL
        """
        # Générer le message à partir du prompt
        messages = self.prompt.invoke({"configs": configs})
        # Appeler le LLM avec les messages générés
        response = self.llm.invoke(messages)
        # Retourner le contenu du résultat
        return response.content if hasattr(response, "content") else response