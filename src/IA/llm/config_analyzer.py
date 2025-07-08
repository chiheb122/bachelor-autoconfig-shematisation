from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate


class ConfigAnalyzerAgent:
    def __init__(self, api_key: str):
        self.llm = init_chat_model("mistral-large-latest", model_provider="mistralai", api_key=api_key)
        # Charger le prompt depuis le fichier
        template_path = Path(__file__).parent / "prompt_template.txt"
        system_template = template_path.read_text()
        # Créer le prompt template avec les nouveaux rôles
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
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