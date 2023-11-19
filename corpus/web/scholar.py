import json
from typing import List
from lodstorage.sparql import SPARQL

class ScholarAPI():
    """
    API service for scholarly data
    """

    def __init__(self, name: str):
        '''
        construct me

        Args:
            name(str): my name
            template_folder(str): the template folder
        '''
        self.name = name

        @self.blueprint.route('/complete', methods=['POST'])
        def completeScholar():
            return self.completeScholar()


    def completeScholar(self):
        """
        completes the given list of scholars
        Assumption: post request contains a list of scholar records
        """
        scholar=Scholar()
        lod=json.loads(request.data)
        lod=scholar.completeScholar(lod)
        return jsonify(lod)


class Scholar(object):
    """
    a scholar
    """

    @staticmethod
    def getSamples():
        samples=[
            {"wikiDataId":"Q54303353",
             "gndId":"",
             "dblpId":"d/StefanDecker",
             "orcid":"0000-0001-6324-7164",
             "linkedInId":"",
             "googleScholarUser":"uhVkSswAAAAJ",
             "homepage":"http://www.stefandecker.org"
             }]
        return samples

    def completeScholar(self, lod:List[dict]) -> List[dict]:
        """
        completes the given list of scholar records by fetching additional information from wikidata
        Args:
            lod: list of scholar records

        Returns:
            list of completed scholar records
        """
        query = """SELECT 
              (GROUP_CONCAT(?_gndId;separator="|") as ?gndId) 
              (GROUP_CONCAT(?_dblpId;separator="|") as ?dblpId) 
              (GROUP_CONCAT(?_orcid;separator="|") as ?orcid) 
              (GROUP_CONCAT(?_linkedInId;separator="|") as ?linkedInId)  
              (GROUP_CONCAT(?_googleScholarUser;separator="|") as ?googleScholarUser) 
              (GROUP_CONCAT(?_homepage;separator="|") as ?homepage)
            WHERE{
              VALUES ?wikiDataId {%s}

              ?wikiDataId wdt:P31 wd:Q5.
              OPTIONAL{ ?wikiDataId wdt:P227 ?_gndId.}
              OPTIONAL{ ?wikiDataId wdt:P2456 ?_dblpId.}
              OPTIONAL{ ?wikiDataId wdt:P1960 ?_googleScholarUser.}
              OPTIONAL{ ?wikiDataId wdt:P6634 ?_linkedInId.}
              OPTIONAL{ ?wikiDataId wdt:P496 ?_orcid.}
              OPTIONAL{ ?wikiDataId wdt:P856 ?_homepage.}
            }
            GROUP BY ?wikiDataId
            """
        sparql = SPARQL("https://query.wikidata.org/sparql")
        # ToDo Handle multiple results for an ID
        completedScholars=[]
        for scholar in lod:
            qId = scholar.get("wikiDataId", None)
            if qId is not None:
                qres = sparql.queryAsListOfDicts(query % f"wd:{qId}")
                if qres is not None and len(qres)>0:
                    completedScholars.append({**scholar, **qres[0]})
        return completedScholars
