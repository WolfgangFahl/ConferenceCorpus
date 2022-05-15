#!/usr/bin/env python3
# WF 2022-04-10
# https://stackoverflow.com/questions/12789396/how-to-get-multiple-counts-with-one-sql-query
def query(source,colNames,delim,indent):
    '''
    create a single query line
    '''
    sql=""
    extraIndent=""
    if delim:
        sql+=(f"{indent}{delim}\n")
        extraIndent="  "
    sql+=f"{indent}{extraIndent}SELECT source,\n"
    sql+=f"{indent}    COUNT(*) AS total,"
    colDelim="\n"
    for colName in colNames:
        sql+=f"{colDelim}{indent}    SUM(CASE WHEN {colName} is not null THEN 1 ELSE 0 END) as {colName}Count"
        colDelim=",\n"
    sql+=f"\n{indent}  FROM event_{source}"""
    sql+=f"\n{indent}  GROUP BY source"
    return sql

def countUnionQuery(name,colNames,indent):
    '''
    create a named union query with the given column Names
    '''
    sql=f"{indent}SELECT source,total"
    for colName in colNames:
        sql+=f",\n{indent}  {colName}Count,{colName}Count*100/total AS '{colName}%'"
    sql+=f"\n{indent}FROM(\n"
    delim=""
    sources=["confref","crossref","dblp","gnd",
    #"or",
    "tibkat","wikicfp","wikidata"]
    for source in sources:
        sql+=(query(source,colNames,delim,indent+"  "))
        delim=f"\n{indent}  UNION"
    sql+=f"\n{indent}) {name}"
    return sql

def main():
    indent=""
    colNames=["acronym","year","ordinal","city","cityWikidataId","country","countryWikidataId"]
    sql=countUnionQuery("counters",colNames,indent)
    print(sql)

if __name__ == '__main__':
    main()
