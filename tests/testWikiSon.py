'''
Created on 2026-11-02

@author: wf
'''
import os
import tempfile
import unittest

from corpus.wikison import WikiSonBackup, WikiSonPage


class TestWikiSon(unittest.TestCase):
    '''
    test the WikiSon template handling on mwparserfromhell
    '''

    wikiText = """{{Event
|Acronym=AAAI 1980
|Title=First National Conference on Artificial Intelligence
|Ordinal=1
|Series=AAAI
|Year=1980
}}
some text
[[Category:Event]]
"""

    def testRecords(self):
        '''
        test extracting the WikiSon records of a page
        '''
        page = WikiSonPage("AAAI 1980", TestWikiSon.wikiText)
        records = page.records("Event")
        self.assertEqual(1, len(records))
        record = records[0]
        self.assertEqual("AAAI 1980", record["Acronym"])
        self.assertEqual("1", record["Ordinal"])
        self.assertEqual("AAAI 1980", record["pageTitle"])
        self.assertEqual([], page.records("EventSeries"))

    def testRecordWithWikiMarkup(self):
        '''
        test the single record access including the markup
        '''
        page = WikiSonPage("AAAI 1980", TestWikiSon.wikiText)
        record = page.record("Event", includeWikiMarkup=True)
        self.assertEqual(TestWikiSon.wikiText, record["wikiMarkup"])
        self.assertIsNone(page.record("EventSeries"))

    def testUpdate(self):
        '''
        test updating a template argument
        '''
        page = WikiSonPage("AAAI 1980", TestWikiSon.wikiText)
        self.assertTrue(page.update("Event", {"TibKatId": "1750751844"}))
        self.assertEqual("1750751844", page.record("Event")["TibKatId"])
        self.assertIn("[[Category:Event]]", page.wikiText)
        self.assertFalse(page.update("Event", {"Ordinal": 2}, overwrite=False))
        self.assertEqual("1", page.record("Event")["Ordinal"])
        self.assertTrue(page.update("Event", {"Ordinal": 2}, overwrite=True))
        self.assertEqual("2", page.record("Event")["Ordinal"])
        self.assertFalse(page.update("EventSeries", {"Acronym": "AAAI"}))

    def testBackup(self):
        '''
        test reading a wiki markup directory
        '''
        with tempfile.TemporaryDirectory() as wikiTextPath:
            with open(os.path.join(wikiTextPath, "AAAI 1980.wiki"), "w", encoding="utf-8") as wikiFile:
                wikiFile.write(TestWikiSon.wikiText)
            backup = WikiSonBackup(wikiTextPath)
            self.assertEqual(["AAAI 1980"], list(backup.pages.keys()))
            lod = backup.lod("Event")
            self.assertEqual(1, len(lod))
            self.assertEqual("AAAI 1980", lod[0]["pageTitle"])
            self.assertEqual([], backup.lod("Event", limit=0))


if __name__ == "__main__":
    unittest.main()
