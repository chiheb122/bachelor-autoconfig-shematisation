from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from pathlib import Path

class ConfigAnalyzerAgent:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="mistral-large-latest",
            api_key=api_key,
            openai_api_base="https://api.mistral.ai/v1"
        )
        template_path = Path(__file__).parent / "prompt_template.txt"
        template = template_path.read_text()
        self.chain = LLMChain(
            prompt=PromptTemplate(template=template, input_variables=["configs"]),
            llm=self.llm
        )

    def analyze_configs(self, configs: str) -> str:
        return self.chain.run(configs=configs)