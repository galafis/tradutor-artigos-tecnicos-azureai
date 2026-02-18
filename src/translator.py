"""
Modulo principal de traducao de artigos tecnicos usando Azure AI.
Utiliza Azure Translator para traducao neural e Azure OpenAI para refinamento terminologico.
"""

import os
import requests
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AzureTranslator:
    """Classe para traducao de artigos tecnicos usando Azure Translator API."""

    def __init__(self):
        self.key = os.getenv("AZURE_TRANSLATOR_KEY")
        self.endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
        self.region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")
        self.api_version = "3.0"

        if not self.key:
            raise ValueError("AZURE_TRANSLATOR_KEY nao configurada nas variaveis de ambiente.")

    def translate_text(self, text: str, target_language: str = "pt-br", source_language: Optional[str] = None) -> str:
        """
        Traduz texto usando Azure Translator API.

        Args:
            text: Texto a ser traduzido
            target_language: Idioma de destino (padrao: pt-br)
            source_language: Idioma de origem (auto-detectado se None)

        Returns:
            Texto traduzido
        """
        url = f"{self.endpoint}/translate?api-version={self.api_version}&to={target_language}"

        if source_language:
            url += f"&from={source_language}"

        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.region,
            "Content-Type": "application/json",
        }

        body = [{"text": text}]

        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        result = response.json()
        return result[0]["translations"][0]["text"]

    def translate_article(self, article_text: str, target_language: str = "pt-br") -> str:
        """
        Traduz um artigo completo, preservando a formatacao Markdown.

        Args:
            article_text: Texto do artigo em Markdown
            target_language: Idioma de destino

        Returns:
            Artigo traduzido com formatacao preservada
        """
        sections = article_text.split("\n\n")
        translated_sections = []

        for section in sections:
            if section.strip():
                if section.strip().startswith("```"):
                    translated_sections.append(section)
                elif section.strip().startswith("#"):
                    header_level = len(section) - len(section.lstrip("#"))
                    header_text = section.lstrip("# ").strip()
                    translated_header = self.translate_text(header_text, target_language)
                    translated_sections.append(f"{'#' * header_level} {translated_header}")
                else:
                    translated_text = self.translate_text(section, target_language)
                    translated_sections.append(translated_text)
            else:
                translated_sections.append(section)

        return "\n\n".join(translated_sections)

    def detect_language(self, text: str) -> dict:
        """
        Detecta o idioma do texto.

        Args:
            text: Texto para detectar idioma

        Returns:
            Dicionario com idioma detectado e confianca
        """
        url = f"{self.endpoint}/detect?api-version={self.api_version}"

        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Ocp-Apim-Subscription-Region": self.region,
            "Content-Type": "application/json",
        }

        body = [{"text": text[:500]}]

        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()

        result = response.json()
        return {
            "language": result[0]["language"],
            "score": result[0]["score"],
        }

    def get_supported_languages(self) -> dict:
        """
        Retorna a lista de idiomas suportados pelo Azure Translator.

        Returns:
            Dicionario com idiomas suportados
        """
        url = f"{self.endpoint}/languages?api-version={self.api_version}&scope=translation"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()["translation"]


if __name__ == "__main__":
    translator = AzureTranslator()

    sample_text = "Azure OpenAI Service provides REST API access to OpenAI's powerful language models."
    translated = translator.translate_text(sample_text)
    print(f"Original: {sample_text}")
    print(f"Traduzido: {translated}")
