'''
Created on 2022-04-06

@author: wf
'''
from tests.basetest import BaseTest
from ptp.parsing import Tokenizer
from ptp.signature import OrdinalCategory, EnumCategory, CountryCategory


class TestSignature(BaseTest):
    '''
    test the signature parsing
    '''
    
    def testOrdinalCategory(self):
        '''
        test ordinal tokenizer
        '''
        tokenizer=Tokenizer([OrdinalCategory()])
        event={
            'eventId':'conf/icwe/icwe2019',
            'acronym':'ICWE 2019',
            'title':'Web Engineering - 19th International Conference, ICWE 2019, Daejeon, South Korea, June 11-14, 2019, Proceedings'
        }
        tokenSequence=tokenizer.tokenize(event['title'], event)
        self.assertEqual(1,len(tokenSequence.matchResults))
        token=tokenSequence.matchResults[0]
        self.assertEqual('Ordinal',token.category.name)
        self.assertEqual("19th",token.tokenStr)
        self.assertEqual(3,token.pos)
        self.assertEqual(19,token.value)
        
    def testCategories(self):
        '''
        check some categories 
        '''
        ocat=OrdinalCategory()
        self.assertEqual(1245,len(ocat.lookupByKey))
        mcat=EnumCategory("month")
        self.assertEqual(12,len(mcat.lookupByKey))

    def testCountryCategory(self):
        '''
        tests country tokenizer
        '''
        tokenizer = Tokenizer([CountryCategory()])
        event = {
            'eventId': 'conf/tamc/tamc2017 ',
            'acronym': 'TAMC 2017',
            'title': 'TAMC 2017 : Theory and Applications of Models of Computation, Bern Switzerland'
        }
        tokenSequence = tokenizer.tokenize(event['title'], event)
        self.assertEqual(1, len(tokenSequence.matchResults))
        token = tokenSequence.matchResults[0]
        self.assertEqual('country', token.category.name)
        self.assertEqual("Switzerland", token.tokenStr)
        self.assertEqual(11, token.pos)
        self.assertEqual("Switzerland", token.value)
