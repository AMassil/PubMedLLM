import unittest

from pubmedllm.pubget_handler import PubgetHandler


class PubgetHandlerTests(unittest.TestCase):
    def test_requires_contact_email_before_network_request(self):
        handler = PubgetHandler("")
        with self.assertRaisesRegex(ValueError, "NCBI_EMAIL"):
            handler.download_papers("cancer", 1)

    def test_validates_query_and_result_count(self):
        handler = PubgetHandler("researcher@example.org")
        with self.assertRaises(ValueError):
            handler.download_papers(" ", 1)
        with self.assertRaises(ValueError):
            handler.download_papers("cancer", 0)


if __name__ == "__main__":
    unittest.main()