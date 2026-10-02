import tempfile
import unittest
from pathlib import Path

from pubmedllm.document_processor import DocumentProcessor


ARTICLE_XML = """\
<pmc-articleset>
  <article>
    <front><article-meta>
      <article-id pub-id-type="pmcid">PMC123</article-id>
      <article-id pub-id-type="pmid">456</article-id>
      <title-group><article-title>A useful title</article-title></title-group>
      <abstract><p>Evidence from the abstract.</p></abstract>
    </article-meta></front>
    <body><sec><title>Results</title><p>A useful result.</p></sec></body>
  </article>
</pmc-articleset>
"""


class DocumentProcessorTests(unittest.TestCase):
    def test_extracts_pmc_xml_text_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "article.xml"
            path.write_text(ARTICLE_XML, encoding="utf-8")

            documents = DocumentProcessor().process_file(str(path))

        self.assertGreaterEqual(len(documents), 1)
        combined = " ".join(document.page_content for document in documents)
        self.assertIn("A useful title", combined)
        self.assertIn("Evidence from the abstract", combined)
        self.assertIn("A useful result", combined)
        self.assertEqual(documents[0].metadata["pmcid"], "PMC123")
        self.assertEqual(documents[0].metadata["pmid"], "456")

    def test_rejects_unsupported_files_without_crashing_batch(self):
        self.assertEqual(DocumentProcessor().process_file("paper.txt"), [])


if __name__ == "__main__":
    unittest.main()