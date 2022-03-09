'''
Created on 2021-08-07

@author: wf
'''

from tests.datasourcetoolbox import DataSourceTest
from corpus.eventtransfer import EventExporter
import getpass            

class TestOpenResearchExport(DataSourceTest):
    '''
    test exporting series and events from the  dblp data source
    '''
 
    def setUp(self):
        '''
        '''
        DataSourceTest.setUp(self)
        pass
  

    def testSeriesExport(self):
        '''
        test exporting a single series
        '''
        # do not run this in CI
        if getpass.getuser()!="wf":
            return
        debug=True
        exporter=EventExporter(debug=debug)
        for acronym in [#'dc'
                        #,'ds'
                        #,'seke','qurator',
                        #'vnc'
                        #'dawak','emnlp','cla'
                        #'ijcnn'
                        #'recsys'
                        #'ideas'
                        'er'
                        #'ice/itmc'
            ]:
            dblpSeriesId=f"{acronym}"
            exportCount=exporter.exportSeries2OpenResearch(dblpSeriesId)
            self.assertTrue(exportCount>0)
            pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    DataSourceTest.main()