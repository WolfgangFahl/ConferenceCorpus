import os.path
import yaml
from collections import Counter, OrderedDict

from ptp.parsing import Tokenizer
from ptp.signature import CityPrefixCategory, CityCategory
from tests.basetest import BaseTest
from tests.testParsing import TestParsing


class TestCityCategory(BaseTest):
    """
    tests CityCategory
    """

    def testCityPrefixCategory(self):
        """
        tests categorization of city prefixes
        """
        testParams = [("Los", '1'), ("de", "1,2"), ("Washington,", "1")]
        cityPrefixCategory = CityPrefixCategory()
        for prefix, expectedPositions in testParams:
            self.assertTrue(cityPrefixCategory.checkMatch(prefix))
            value = cityPrefixCategory.itemFunc(prefix)
            self.assertEqual(expectedPositions, value)

    def testCityCategory(self):
        """
        tests tokenization of cities with the CityCategory
        """
        tokenizer = Tokenizer([CityPrefixCategory(),CityCategory()])
        testParams = [
            ("Q1297", "Proceedings of the Twenty-Third AAAI Conference on Artificial Intelligence and the Twentieth Innovative Applications of Artificial Intelligence Conference : 13-17 July 2008, Chicago, Illinois, USA ; Vol. 2"),
            ("Q65", "12th IEEE International Conference on Nano/Micro Engineered and Molecular Systems, NEMS 2017, Los Angeles, CA, USA, April 9-12, 2017"),
            ("Q8678", "1st Latin American Network Operations and Management Symposium, LANOMS 1999, Rio de Janeiro, Brazil, December 3-5, 1999"),
            ("Q60","1960 proceedings of Instrument Society of America 15th Annual Instrument-Automation Conference and Exhibit, New York City, New York, September 26 - 30, 1960 ; Pt. 2")
        ]
        for expectedValue, title in testParams:
            tokenSequence = tokenizer.tokenize(title, f"test_for_{expectedValue}")
            matchedCities = tokenSequence.getTokenOfCategory("city")
            self.assertEqual(1, len(matchedCities))
            self.assertEqual(expectedValue, matchedCities[0].value)

    def testGeneratePrefixYaml(self):
        """
        generates the prefix yaml for city names
        """
        citiesYamlPath = "/tmp/cities.yaml"
        if not os.path.isfile(citiesYamlPath):
            TestParsing().testCreateLookup()
        with open(citiesYamlPath, mode="r") as fp:
            cities = yaml.safe_load(fp)
        cityNames = {name for name in cities.keys()}
        print("Number of distinct city names", len(cityNames))
        print("City name parts distribution", Counter([len(name.split(" ")) for name in cityNames]))
        prefixes = {}
        for name in cityNames:
            nameParts = name.split(" ")
            numberOfParts = len(nameParts)
            if numberOfParts > 1:
                for i, namePart in enumerate(nameParts[:-1]):
                    self.addToDictList(prefixes, namePart, numberOfParts-i-1, distinct=True)
        prefixes = dict(OrderedDict(sorted(prefixes.items())))
        print(prefixes)
        prefixYaml = {prefix:{"value": ",".join({str(pos) for pos in positions})} for prefix, positions in prefixes.items()}
        citiesYaml = {
            name: {
                "type": "city",
                "value": record.get("qid")
            }
            for name, record in cities.items()
        }
        with open("/tmp/cityNamePrefixes.yaml", mode="w") as fp:
            desc = """#\n# City name prefix directory\n# the value describes the positions the prefix occurs (from the perspective of the last name part)\n#\n"""
            fp.write(desc)
            yaml.dump(prefixYaml, fp)
        with open("/tmp/cityNames.yaml", mode="w") as fp:
            desc = """#\n# City directory\n#\n"""
            fp.write(desc)
            yaml.dump(citiesYaml, fp)

    @staticmethod
    def addToDictList(d:dict, key:str, value, distinct:bool=False):
        if key in d:
            if isinstance(d[key], list):
                d[key].append(value)
            elif isinstance(d[key], set):
                d[key].add(value)
            else:
                raise Exception("Given dictionary has incorrect format")
        else:
            if distinct:
                valueInSet = set()
                valueInSet.add(value)
                d[key] = valueInSet
            else:
                d[key] = [value]

