import unittest
import fetch

class TestFetch(unittest.TestCase):
    def test_fetch_rows(self):
        rows = fetch.fetch_rows()
        self.assertIsInstance(rows, list)
        self.assertTrue(all(isinstance(row, list) for row in rows))
        self.assertGreater(len(rows), 0, "No rows fetched from source")
        self.assertEqual(len(rows[0]), len(fetch.HEADERS), "Row length does not match headers")

    def test_infer_region(self):
        self.assertEqual(fetch.infer_region("USA"), "USA")
        self.assertEqual(fetch.infer_region("Canada"), "Canada")
        self.assertEqual(fetch.infer_region("Germany"), "EU")
        self.assertEqual(fetch.infer_region("Brazil"), "Other")

    def test_clean(self):
        self.assertEqual(fetch.clean("  test  "), "test")
        self.assertEqual(fetch.clean("\nnew\tline\t"), "new line")
        self.assertEqual(fetch.clean("") , "")

if __name__ == "__main__":
    unittest.main()
