from core.scraper import ArticlePage
from openai import OpenAI


class Extractor:
    def __init__(self, systemPrompt, extractPrompt, filterPrompt):
        self.client = OpenAI()
        self.systemPrompt = systemPrompt
        self.extractPrompt = extractPrompt
        self.filterPrompt = filterPrompt

    def extract(
        self, article: ArticlePage
    ) -> str | None:  # TODO create a valid output class
        systemPrompt = {"role": "system", "content": self.systemPrompt}
        filterPrompt = {
            "role": "user",
            "content": f"{self.filterPrompt}\n\n{article.title}",
        }
        extractPrompt = {
            "role": "user",
            "content": f"{self.extractPrompt}\n\n{article.content}",
        }

        filterCheckOutput = self.client.responses.create(
            model="gpt-4o", input=[systemPrompt, filterPrompt]
        )

        print("Filter Check:", filterCheckOutput.output_text)

        if "no" in filterCheckOutput.output_text.lower():
            return None

        featuresOutput = self.client.responses.create(
            model="gpt-4o",
            input=[systemPrompt, extractPrompt],
        )

        return featuresOutput.output_text
