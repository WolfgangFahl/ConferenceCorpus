import getpass
import os
from os import path
from wikibot.wikiuser import WikiUser
from wikifile.wikiFileManager import WikiFileManager


class TestSMW:
    '''
    tests functionalities of the smw package
    provides helper functions for other tests
    '''
    wikiId = 'orclone'

    @staticmethod
    def inPublicCI():
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in ["travis", "runner"];

    @classmethod
    def getWikiUser(cls, wikiId=None):
        if wikiId is None:
            wikiId = cls.wikiId
        # make sure there is a wikiUser (even in public CI)
        wikiUser = cls.getSMW_WikiUser(wikiId=wikiId, save=cls.inPublicCI())
        return wikiUser

    @classmethod
    def getSMW_WikiUser(cls, wikiId="or", save=False):
        '''
        get semantic media wiki users for SemanticMediawiki.org and openresearch.org
        '''
        iniFile = WikiUser.iniFilePath(wikiId)
        wikiUser = None
        if not os.path.isfile(iniFile):
            wikiDict = None
            if wikiId == "or":
                wikiDict = {"wikiId": wikiId, "email": "noreply@nouser.com", "url": "https://www.openresearch.org",
                            "scriptPath": "/mediawiki/", "version": "MediaWiki 1.31.1"}
            if wikiId == "orclone":
                wikiDict = {"wikiId": wikiId, "email": "noreply@nouser.com",
                            "url": "https://confident.dbis.rwth-aachen.de", "scriptPath": "/or/",
                            "version": "MediaWiki 1.35.1"}
            if wikiId == "cr":
                wikiDict = {"wikiId": wikiId, "email": "noreply@nouser.com", "url": "https://cr.bitplan.com",
                            "scriptPath": "/", "version": "MediaWiki 1.33.4"}

            if wikiDict is None:
                raise Exception("wikiId %s is not known" % wikiId)
            else:
                wikiUser = WikiUser.ofDict(wikiDict, lenient=True)
                if save:
                    wikiUser.save()
        else:
            wikiUser = WikiUser.ofWikiId(wikiId, lenient=True)
        return wikiUser

    @classmethod
    def getWikiFileManager(cls, wikiId=None, debug=False):
        wikiUser = cls.getWikiUser(wikiId)
        home = path.expanduser("~")
        wikiTextPath = f"{home}/.or/wikibackup/{wikiUser.wikiId}"
        wikiFileManager = WikiFileManager(wikiId, wikiTextPath, login=False, debug=debug)
        return wikiFileManager