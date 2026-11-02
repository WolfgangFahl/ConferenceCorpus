'''
Created on 2026-11-02

WikiSon template handling on mwparserfromhell - replaces the wikirender/wikifile dependency

@author: wf
'''
import os
from typing import Dict, List, Optional

import mwparserfromhell


class WikiSonPage(object):
    '''
    a page of wiki markup carrying WikiSon template records
    '''

    def __init__(self, pageTitle: str, wikiText: str, wikiId: str = None):
        '''
        constructor

        Args:
            pageTitle(str): the title of the page
            wikiText(str): the wiki markup of the page
            wikiId(str): the id of the wiki the page belongs to
        '''
        self.pageTitle = pageTitle
        self.wikiText = wikiText
        self.wikiId = wikiId

    @classmethod
    def ofFile(cls, path: str) -> "WikiSonPage":
        '''
        read a page from a wiki markup file

        Args:
            path(str): the path of the .wiki file

        Returns:
            WikiSonPage: the page with the pageTitle taken from the file name
        '''
        with open(path, encoding="utf-8") as wikiFile:
            wikiText = wikiFile.read()
        pageTitle = os.path.basename(path)
        suffix = ".wiki"
        if pageTitle.endswith(suffix):
            pageTitle = pageTitle[:-len(suffix)]
        return cls(pageTitle, wikiText)

    @classmethod
    def ofWiki(cls, wikiId: str, pageTitle: str) -> "WikiSonPage":
        '''
        read a page from a wiki

        Args:
            wikiId(str): the id of the wiki to read from
            pageTitle(str): the title of the page to read

        Returns:
            WikiSonPage: the page with the markup of the wiki
        '''
        from wikibot3rd.wikiclient import WikiClient
        wikiClient = WikiClient.ofWikiId(wikiId)
        wikiText = wikiClient.getWikiMarkup(pageTitle)
        return cls(pageTitle, wikiText, wikiId=wikiId)

    def templates(self, templateName: str) -> List:
        '''
        get the parsed templates of the given name

        Args:
            templateName(str): the name of the WikiSon entity

        Returns:
            list: the mwparserfromhell templates with that name
        '''
        parsed = mwparserfromhell.parse(self.wikiText)
        return self.templatesOf(parsed, templateName)

    @staticmethod
    def templatesOf(parsed, templateName: str) -> List:
        '''
        get the templates of the given name from the given parsed markup

        Args:
            parsed: the mwparserfromhell parse result
            templateName(str): the name of the WikiSon entity

        Returns:
            list: the templates with that name
        '''
        name = templateName.strip()
        return [template for template in parsed.filter_templates()
                if str(template.name).strip() == name]

    def records(self, templateName: str) -> List[Dict]:
        '''
        get the WikiSon records of the given template name

        Args:
            templateName(str): the name of the WikiSon entity

        Returns:
            list: a list of dicts, each carrying the template arguments and the pageTitle
        '''
        lod = []
        for template in self.templates(templateName):
            record = {}
            for param in template.params:
                record[str(param.name).strip()] = str(param.value).strip()
            if record:
                record["pageTitle"] = self.pageTitle
                lod.append(record)
        return lod

    def record(self, templateName: str, includeWikiMarkup: bool = False) -> Optional[Dict]:
        '''
        get the single WikiSon record of the given template name

        Args:
            templateName(str): the name of the WikiSon entity
            includeWikiMarkup(bool): if True add the markup of the page as wikiMarkup

        Returns:
            dict: the last record of that template or None if the page carries none
        '''
        lod = self.records(templateName)
        if not lod:
            return None
        record = lod[-1]
        if includeWikiMarkup:
            record["wikiMarkup"] = self.wikiText
        return record

    def update(self, templateName: str, args: Dict, overwrite: bool = True) -> bool:
        '''
        update the arguments of the templates of the given name

        Args:
            templateName(str): the name of the WikiSon entity
            args(dict): the arguments to set
            overwrite(bool): if True replace values that are already set

        Returns:
            bool: True if the markup was changed
        '''
        parsed = mwparserfromhell.parse(self.wikiText)
        updated = False
        for template in self.templatesOf(parsed, templateName):
            for key, value in args.items():
                if value is None:
                    continue
                if template.has(key) and not overwrite:
                    continue
                template.add(key, str(value))
                updated = True
        if updated:
            self.wikiText = str(parsed)
        return updated

    def push(self, msg: str = None, wikiId: str = None):
        '''
        push the markup of this page to its wiki

        Args:
            msg(str): the summary to show in the page history
            wikiId(str): the id of the wiki to push to - defaults to the wiki the page came from
        '''
        from wikibot3rd.wikiclient import WikiClient
        pushWikiId = wikiId if wikiId is not None else self.wikiId
        if pushWikiId is None:
            raise ValueError(f"no wikiId to push {self.pageTitle} to")
        wikiClient = WikiClient.ofWikiId(pushWikiId)
        wikiClient.savePage(self.pageTitle, self.wikiText, msg)


class WikiSonBackup(object):
    '''
    a directory of wiki markup files as created by the wikibackup script
    '''

    def __init__(self, wikiTextPath: str):
        '''
        constructor

        Args:
            wikiTextPath(str): the root of the wiki markup directory
        '''
        self.wikiTextPath = wikiTextPath
        self.pages = {}
        for root, _dirnames, fileNames in os.walk(wikiTextPath):
            for fileName in fileNames:
                if fileName.endswith(".wiki"):
                    page = WikiSonPage.ofFile(os.path.join(root, fileName))
                    self.pages[page.pageTitle] = page

    def lod(self, templateName: str, limit: int = None) -> List[Dict]:
        '''
        get the WikiSon records of the given template name of all pages

        Args:
            templateName(str): the name of the WikiSon entity
            limit(int): the maximum number of records to return

        Returns:
            list: a list of dicts
        '''
        lod = []
        for page in self.pages.values():
            for record in page.records(templateName):
                if limit is not None and len(lod) >= limit:
                    return lod
                lod.append(record)
        return lod
