import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pubmedllm.rag_system import PubmedLLM
from tests.test_document_processor import ARTICLE_XML


class FakeVectorStore:
    def __init__(self):
        self.documents = []
        self.ids = []

    def add_documents(self, documents, ids):
        self.documents.extend(documents)
        self.ids.extend(ids)

    def similarity_search(self, _query, k):
        del _query
        return self.documents[:k]


class FakeLlm:
    def __init__(self):
        self.messages: list[tuple[str, str]] | None = None

    def invoke(self, messages):
        self.messages = messages
        return SimpleNamespace(text="Supported answer [Source 1].")


class RagSystemTests(unittest.TestCase):
    def make_system(self):
        vectorstore = FakeVectorStore()
        llm = FakeLlm()
        system = PubmedLLM(embeddings=object(), llm=llm, vectorstore=vectorstore)
        return system, vectorstore, llm

    def test_indexes_and_queries_with_cited_context(self):
        system, vectorstore, llm = self.make_system()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.xml"
            path.write_text(ARTICLE_XML, encoding="utf-8")
            indexed = system.index_documents([str(path)])

        result = system.query("What was found?")

        self.assertEqual(indexed, len(vectorstore.documents))
        self.assertGreater(indexed, 0)
        self.assertEqual(len(vectorstore.ids), len(set(vectorstore.ids)))
        self.assertEqual(result["result"], "Supported answer [Source 1].")
        self.assertIsNotNone(llm.messages)
        assert llm.messages is not None
        self.assertIn("[Source 1: A useful title]", llm.messages[1][1])

    def test_returns_clear_result_when_store_is_empty(self):
        system, _, llm = self.make_system()

        result = system.query("Unknown question")

        self.assertEqual(result["source_documents"], [])
        self.assertIn("No relevant document", result["result"])
        self.assertIsNone(llm.messages)

    def test_download_requires_indexable_articles(self):
        system, _, _ = self.make_system()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(system.pubget_handler, "download_papers", return_value=directory):
                with self.assertRaisesRegex(RuntimeError, "no text could be indexed"):
                    system.download_and_index_papers("test", 1)


if __name__ == "__main__":
    unittest.main()