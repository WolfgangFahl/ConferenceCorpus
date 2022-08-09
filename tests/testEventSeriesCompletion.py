import re
from typing import Dict

import tabulate
from lodstorage.lod import LOD

from corpus.eventseriescompletion import EventSeriesCompletion, TitleScore
from corpus.lookup import CorpusLookup
from tests.basetest import BaseTest
import json
from os import path
from ptp.ordinal import Ordinal

class TestEventSeriesCompletion(BaseTest):
    """
    tests EventSeriesCompletion
    """

    def setUp(self,debug=False,profile=True):
        self.lookup = CorpusLookup()
        self.testSeriesAcronyms = ['3DUI', 'AAAI', 'AAMAS', 'ACCV', 'ACHI', 'ACII', 'ACIIDS', 'ACISP', 'ACIVS', 'ACL',
                                   'ACNS', 'ACSAC', 'ADBIS', 'ADHOC-NOW', 'ADMA', 'AIED', 'AIME', 'AINA', 'AISC',
                                   'AIVR', 'AMCIS', 'AMTA', 'AMW', 'ANSS', 'ANTS', 'ARES', 'ASE', 'ASPLOS', 'BCS HCI',
                                   'BDA', 'BICoB', 'BIOSIGNALS', 'BIS', 'BTW', 'CAIP', 'CANS', 'CAiSE', 'CC', 'CCC',
                                   'CCGRID', 'CCS', 'CDC', 'CEC', 'CGO', 'CHI', 'CIAA', 'CIKM', 'CLA', 'CMCS', 'COCOON',
                                   'COLING', 'COLT', 'COMAD', 'COMPSAC', 'CRIS', 'CRYPTO', 'CSCW', 'CSF', 'CSL', 'CSR',
                                   'CVPR', 'Complex', 'CoopIS', 'DAC', 'DCC', 'DCMI', 'DCOSS', 'DEBS', 'DGO', 'DIS',
                                   'DL', 'DMS', 'DS', 'DaWaK', 'ECAI', 'ECCE', 'ECCV', 'ECDL', 'ECIS', 'EKAW', 'EMCIS',
                                   'EMNLP', 'ENASE', 'EPIA', 'ER', 'ESEC', 'ESOP', 'ESSCIRC', 'ESWC', 'ETAPS', 'FASE',
                                   'FCT', 'FOCS', 'FOSSACS', 'FQAS', 'FSE', 'FUN', 'FUSION', 'GD', 'GECCO', 'GLOBECOM',
                                   'GPCE', 'GameSec', 'H-WORKLOAD', 'HOTI', 'HPCC', 'HPDC', 'HRI', 'HSCC', 'HiPC',
                                   'Humanoids', 'I-SEMANTICS', 'IC3K', 'ICAC', 'ICADL', 'ICALP', 'ICALT', 'ICANN',
                                   'ICASSP', 'ICC', 'ICCCI', 'ICCS', 'ICCV', 'ICDAR', 'ICDE', 'ICDSC', 'ICEBE',
                                   'ICEIS', 'ICGSE', 'ICIAP', 'ICIAR', 'ICIP', 'ICIQ', 'ICML', 'ICMR', 'ICMT-1', 'ICPE',
                                   'ICRA', 'ICRE', 'ICS', 'ICSC', 'ICSE', 'ICWE', 'ICWS', 'IDEAS',
                                   'IEEE BigDataService', 'IEEE Cluster', 'IEEE ECCE', 'IJCAI', 'IJCNLP', 'IJCNN',
                                   'IMC', 'INLG', 'INTERSPEECH', 'IPDPS', 'IPEC', 'IPMU', 'IRCDL', 'ISI', 'ISIWI',
                                   'ISMAR', 'ISMM', 'ISPA', 'ISPASS', 'ISSI', 'ISWC', 'IUI', 'JCDL', 'JIST', 'K-CAP',
                                   'KDD', 'KEOD', 'KES-AMSTA', 'KESW', 'KR', 'Konvens', 'LAK', 'LDOW', 'LESS', 'LICS',
                                   'LPAR', 'LREC', 'MM', 'MMM', 'MTSR', 'NAACL', 'NAACL HLT', 'NIPS', 'OM', 'OOPSLA',
                                   'OPENSYM', 'OPODIS', 'OSDI', 'PACIS', 'PAKDD', 'PLDI', 'PLOP', 'PODC', 'PODS',
                                   'POPL', 'PRICAI', 'QoSA', 'Qurator', 'RCDL', 'RE', 'REFSQ', 'RO-MAN', 'RSS',
                                   'RecSys', 'SAC', 'SAGT', 'SDM', 'SEKE', 'SIGIR', 'SIGMOD', 'SLATE', 'SMC', 'SOFSEM',
                                   'SSDBM', 'SemWiki', 'SenSys', 'TACAS', 'TAMC', 'TPDL', 'TREC', 'UIST', 'UbiComp',
                                   'VISAPP', 'VLDB', 'VNC', 'VR', 'WEBIST', 'WIMS', 'WINE', 'WISE', 'WPNC', 'WSDM',
                                   'WWW', 'Web Intelligence', 'XP', 'XSym', 'ZEUS']
        super().setUp(debug=debug, profile=profile)
    
    def getSeriesLod(self,seriesAcronym:str):
        '''
        get a list of dicts for a series for some test cases
        '''
        home = path.expanduser("~")
        cachedir= f"{home}/.conferencecorpus/esctestdata"
        with open(f'{cachedir}/{seriesAcronym}.json') as json_file:
            seriesData = json.load(json_file)
            return seriesData

    def querySeriesLod(self, seriesAcronym:str) -> Dict[str,dict]:
        """
        queries for the given seriesAcronym
        Args:
            seriesAcronym: acronym of the series

        Returns:
            dict of dicts
        """
        multiQuery = "SELECT * FROM {event}"
        idQuery = f"""SELECT source,eventId FROM event WHERE lookupAcronym LIKE "{seriesAcronym} %" ORDER BY year DESC"""
        res = self.lookup.getDictOfLod4MultiQuery(multiQuery, idQuery)
        return res

        
    def testParseOrdinal(self):
        '''
        check the parsing of ordinals
        '''
        title='12th IEEE International Symposium on Wearable Computers (ISWC 2008), September 28 - October 1, 2008, Pittsburgh, PA, USA'
        item="irrelevant"
        pol=Ordinal.parseOrdinals(title, item)
        debug=self.debug
        #debug=True
        if (debug):
            print(pol)
        self.assertEqual([12],pol)
        
    def testGuessOrdinal(self):
        '''
        test guessing the ordinal
        '''
        seriesIds = ["VLDB"]
        for seriesId in seriesIds:
            seriesLod = self.getSeriesLod(seriesId)
            for event in seriesLod:
                Ordinal.addParsedOrdinal(event)
            if self.debug:
                print(f"Series {seriesId} (sorted)")        
            seriesLodByOrdinal = sorted(seriesLod,key=lambda event: event.get("ordinal", 0))
            for event in seriesLodByOrdinal:
                if self.debug:
                    ordinal = event.get("ordinal", "?")
                    year = event.get("year", "?")
                    source = event.get("source")
                    print(f"""{ordinal}:{year}-{source}{event}""")
                
       
    def testMergingSeries(self):
        '''
        test merging event series from different sources
        '''
        vldbSeriesLod=self.getSeriesLod("VLDB")
        if self.debug:
            # print (vldbSeriesLod)
            print (len(vldbSeriesLod))
            
        vldbSeriesLod=sorted(vldbSeriesLod,key=lambda event:event["year"] if event.get("year") in event else 0)
        for vldbEvent in vldbSeriesLod:
            if vldbEvent["year"] is  not None:
                if self.debug:
                    year = vldbEvent["year"]
                    source = vldbEvent["source"]
                    print(f"{year}: {source}")

    def test_getCompletedBlankSeries(self):
        """
        tests getCompletedBlankSeries
        extraction and completion of an event series for ordinal and year pairs
        """
        seriesLod = self.getSeriesLod("AAAI")
        completedBlankSeries = EventSeriesCompletion.getCompletedBlankSeries(seriesLod)
        # vldbSeriesLod has multiple records with same year but different ordinal → expect None
        self.assertEqual([], completedBlankSeries)
        seriesLod = self.getSeriesLod("VLDB")
        completedBlankSeries = EventSeriesCompletion.getCompletedBlankSeries(seriesLod)
        self.assertEqual(46, len(completedBlankSeries))  # CI has 46 my local db has 47???
        self.assertEqual((1975, 1), completedBlankSeries[0])
        self.assertEqual((2020, 46), completedBlankSeries[-1])
        seriesLod = self.getSeriesLod("3DUI")
        completedBlankSeries = EventSeriesCompletion.getCompletedBlankSeries(seriesLod)
        self.assertEqual(12, len(completedBlankSeries))
        self.assertEqual((2006,1), completedBlankSeries[0])
        self.assertEqual((2017,12), completedBlankSeries[-1])

    def test_getFrequency(self):
        """
        tests getFrequency
        """
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2004, 5), (2005, 5)]))
        self.assertEqual(1,EventSeriesCompletion.getFrequency([(2000, 1), (2001, 2), (2002,3)]))
        self.assertEqual(2, EventSeriesCompletion.getFrequency([(2000, 1), (2002, 2), (2004, 3)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2001, 2), (2004, 3)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2001, 5), (2002, 3)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2000, 1), (2002, 2), (2004, 3), (2005,4), (2006, 5)]))
        self.assertEqual(0, EventSeriesCompletion.getFrequency([(2011, 2), (2013, 2), (2015, 4), (2016, 5), (2017, 6), (2018, 7), (2019, 8), (2020, 9), (2021, 10)]))

    def testAnalyzeTibkatDuplicateEntries(self):
        """
        analyzes tibkat series entries
        """
        return
        volumeRegexp = r'\[?[Vv]ol\.\]?( |)(?P<volumeNumber>\d{1,2}|[A-H]|(IX|IV|V?I{1,3}))'
        res = []
        for seriesAcronym in self.testSeriesAcronyms:
            seriesRes = {"series": seriesAcronym}
            lod = self.querySeriesLod(seriesAcronym).get("tibkat")
            if lod is None:
                continue
            byYear = LOD.getLookup(lod, attrName="year", withDuplicates=True)
            byOrd = LOD.getLookup(lod, attrName="ordinal", withDuplicates=True)
            seriesRes["#Records"]=len(lod)
            seriesRes["uniqueRecordsByYear"]=len(byYear)
            seriesRes["uniqueRecordsByOrdinal"] = len(byOrd)
            seriesRes["#OfOrdsWithMultipleRecords"] = sum([1 if len(v) > 1 else 0 for v in byOrd.values()])
            seriesRes["#MultipleRecords"] = sum([len(v) if len(v)>1 else 0 for v in byOrd.values()])
            seriesRes["#ProceedingsInTitle"] = len([True for d in lod if d.get("title", "") and "proceedings" in d.get("title", "").lower()])
            seriesRes["#VolumeInTitle"] = len([True for d in lod if len(byOrd.get(d.get("ordinal"), [])) > 1 and d.get("title", "") and re.search(volumeRegexp,d.get("title", ""))])
            filteredLod = EventSeriesCompletion.filterDuplicatesByTitle(lod, debug=False)
            seriesRes["#deduplicatedRecords"] = len(filteredLod)
            res.append(seriesRes)
        print(tabulate.tabulate(res, headers="keys", tablefmt="mediawiki"))

    def testFilterDuplicates(self):
        """
        tests filtering of duplicate records
        """
        seriesAcronym = "ACCV"
        seriesRecords = self.querySeriesLod(seriesAcronym).get("tibkat")
        res = EventSeriesCompletion.filterDuplicatesByTitle(seriesRecords)
        if self.debug:
            print("Reduced:", len(seriesRecords), "→", len(res))
        self.assertLessEqual(140,len(seriesRecords))
        self.assertGreaterEqual(20, len(res))

    def testTitleScore(self):
        """
        tests scoring of event titles
        """
        titles = [
            'Now accepting video submissions : [... best of the Sixth Asian Conference on Computer Vision (ACCV2004) ... was held from 28 - 30 January 2004 in Jeju Island, Korea ...]',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8 - 12, 2010 ; revised selected papers, part III',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8 - 12, 2010 ; revised selected papers, part IV',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8 - 12, 2010 ; revised selected papers, part II',
            'Computer vision - ACCV 2010 workshops : ACCV 2010 international workshops, Queenstown, New Zealand, November 8 - 9, 2010 ; revised selected papers, part I',
            'Computer vision - ACCV 2010 workshops : ACCV 2010 international workshops, Queenstown, New Zealand, November 8 - 9, 2010 ; revised selected papers, part II',
            'Computer vision - ACCV 2010 workshops : ACCV 2010 international workshops, Queenstown, New Zealand, November 8-9, 2010; revised selected papers / Reinhard Koch; Fay Huang (eds.) ; Pt. 2',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8 - 12, 2010 ; revised selected papers, part I',
            'Computer vision - ACCV 2010 workshops : ACCV 2010 international workshops, Queenstown, New Zealand, November 8-9, 2010; revised selected papers / Reinhard Koch; Fay Huang (eds.) ; Pt. 1',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8-12, 2010; revised selected papers / Ron Kimmel; Reinhard Klette; Akihiro Sugimoto (eds.) ; Pt. 4',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8-12, 2010; revised selected papers / Ron Kimmel; Reinhard Klette; Akihiro Sugimoto (eds.) ; Pt. 1',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8-12, 2010; revised selected papers / Ron Kimmel; Reinhard Klette; Akihiro Sugimoto (eds.) ; Pt. 2',
            'Computer vision - ACCV 2010 : 10th Asian Conference on Computer Vision, Queenstown, New Zealand, November 8-12, 2010; revised selected papers / Ron Kimmel; Reinhard Klette; Akihiro Sugimoto (eds.) ; Pt. 3'
        ]
        for title in titles:
            if self.debug:
                print(TitleScore.getScore(title), title)

        verifyTitleScore = [
            (1.5, "volume 1"),
            (1, "volume 2"),
            (3.5, "Proceedings of the 10th Asian Conference on Computer Vision volume 1")
        ]
        for expectedScore, title in verifyTitleScore:
            self.assertEqual(expectedScore, TitleScore.getScore(title))