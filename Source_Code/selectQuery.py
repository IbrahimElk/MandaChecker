from multiprocessing import resource_tracker
import SPARQLWrapper as sp 
import json 

sparql = sp.SPARQLWrapper("https://qa.centrale-vindplaats.lblod.info/sparql")
sparql.setReturnFormat(sp.JSON)


def main():
    pass


def getAllSittingsFromEveryBestuursEenheid(AantalZittingen):
     # alle namen van gemeenteraad alken    
    x = "\"" + "notulen" + "\""
    y = "\"" + "bestuursorganen" + "\""

    if (AantalZittingen > 0):
        z = "LIMIT " + str(AantalZittingen)
    else : 
        z = " "
        
    sparql.setQuery("""
        PREFIX http: <http://www.w3.org/2011/http#>
        PREFIX prov: <http://www.w3.org/ns/prov#> 
        PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX org: <http://www.w3.org/ns/org#>
        PREFIX gen: <https://data.vlaanderen.be/ns/generiek>
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
        PREFIX lblodlg: <http://data.lblod.info/vocabularies/leidinggevenden/>

        SELECT ?zitting ?linkNaarDieZitting ?bestuursorgaanUri
        WHERE {
                ?zitting besluit:isGehoudenDoor ?bestuursorgaanUri.
                ?zitting <http://www.w3.org/2002/07/owl#sameAs> ?linkNaarDieZitting.
                FILTER CONTAINS(STR(?linkNaarDieZitting), """ + x + """).
                FILTER CONTAINS(STR(?bestuursorgaanUri), """ + y + """).

        } """ + z + """

    """) 
    #TODO veralgemene, ENKEL NOTULEN WORDEN GEEXTRAHEERD en ENKEL BESTUURSORGANEN met "bestuursorganen" in de uri !(wegens error)!!! ZIE FILTER HIERBOVEN

    result = sparql.query().convert()
    # with open("data1.json","w") as filefornow:
    #     json.dump(result,filefornow)

    alleZittingUrls = {}
    for item in result["results"]["bindings"]:
        eenZitting = item["zitting"]["value"]
        linkNaarDiezitting = item["linkNaarDieZitting"]["value"]
        Bestuursorgaan = item["bestuursorgaanUri"]["value"]
        alleZittingUrls[eenZitting] = [linkNaarDiezitting, Bestuursorgaan, {}] #derde element (dict) in de lijst, allemaal die ontbreken van die zitting
    return alleZittingUrls   


def GetAllAanwezigeQuery(zitting):
    # is een uri van een zitting
    counter = 0
    sparql.setQuery("""
        PREFIX http: <http://www.w3.org/2011/http#>
        PREFIX prov: <http://www.w3.org/ns/prov#> 
        PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX org: <http://www.w3.org/ns/org#>
        PREFIX gen: <https://data.vlaanderen.be/ns/generiek>
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
        PREFIX lblodlg: <http://data.lblod.info/vocabularies/leidinggevenden/>

        SELECT ?naam ?achternaam
        WHERE {
        <""" + zitting + """> besluit:heeftAanwezigeBijStart ?mandatarisUri. 
        ?mandatarisUri mandaat:isBestuurlijkeAliasVan ?persoonUri.
            ?persoonUri persoon:gebruikteVoornaam ?naam ;
            foaf:familyName ?achternaam .
        }

    """)
    result = sparql.query().convert()

# with open("data" + str(counter) + ".json","w") as filefornow:
#      json.dump(result,filefornow)

    AlleAanweizgen =[]
    for item in result["results"]["bindings"]:
        eenNaam = item["naam"]["value"]
        eenAchternaam = item["achternaam"]["value"]
        volledigeNaam = eenNaam + " " + eenAchternaam  #om later zo te vergelijken met namen met webpage, die zijn ook onderscheden met een ' '
        AlleAanweizgen.append(volledigeNaam)
        #TODO ipv string terug te geven, geef lijst terug [voornaam, achternaam]

    return AlleAanweizgen


def GetTijdelijkeBestuursOrgaan(BestuursOrgaan):
    sparql.setQuery("""
    PREFIX http: <http://www.w3.org/2011/http#>
    PREFIX prov: <http://www.w3.org/ns/prov#> 
    PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
    PREFIX org: <http://www.w3.org/ns/org#>
    PREFIX gen: <https://data.vlaanderen.be/ns/generiek>
    PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
    PREFIX lblodlg: <http://data.lblod.info/vocabularies/leidinggevenden/>

    SELECT ?bestuursorgaanPeriodUri
    WHERE {
        ?bestuursorgaanPeriodUri mandaat:isTijdspecialisatieVan <""" + BestuursOrgaan + """>.
        {SELECT (max(?bindingStartDatum) AS ?RecentsteDatum)
            WHERE { 
                ?bestuursorgaanPeriodUri mandaat:isTijdspecialisatieVan <""" + BestuursOrgaan + """>;
                mandaat:bindingStart ?bindingStartDatum.
            }
        }
        ?bestuursorgaanPeriodUri mandaat:bindingStart ?RecentsteDatum. 
    }""")
    result = sparql.query().convert()

    mandaatnaam = ""
    for item in result["results"]["bindings"]:  
        mandaatnaam = item["bestuursorgaanPeriodUri"]["value"] #kan meer dan 1 mandataris hebben.
    return mandaatnaam


def GetMandatarissenPerson(listOfNames,eenZitting,Everything):
    BestuursOrgaan = Everything[eenZitting][1]
    BestuursOrgaanInPeriode = GetTijdelijkeBestuursOrgaan(BestuursOrgaan)
    # get mandatrisUri from personnames
    Dict = {}
    for name in listOfNames:
        x = "\"" + name.split()[0] + "\"" # bad idea, what if achternaam, in meer dan 1 stuk, bv. Van der waels, dan enkel "Van" als achternaam
        y = "\"" + name.split()[1] + "\"" #TODO ipv string, gebruik lijst [voornaam, achternaam]


        sparql.setQuery("""
            PREFIX http: <http://www.w3.org/2011/http#>
            PREFIX prov: <http://www.w3.org/ns/prov#> 
            PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
            PREFIX org: <http://www.w3.org/ns/org#>
            PREFIX gen: <https://data.vlaanderen.be/ns/generiek>
            PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
            PREFIX lblodlg: <http://data.lblod.info/vocabularies/leidinggevenden/>

            SELECT DISTINCT ?mandatarisUri
            WHERE {
                    <""" + BestuursOrgaanInPeriode + """> org:hasPost ?mandaat.
                    ?mandatarisUri org:holds ?mandaat.
                    ?mandatarisUri mandaat:isBestuurlijkeAliasVan ?persoonUri.
                    ?persoonUri persoon:gebruikteVoornaam """ + x + """ .
                    ?persoonUri foaf:familyName """ + y + """ .
            }

        """)
        result = sparql.query().convert()
        # with open("data1.json","w") as filefornow:
        #     json.dump(result,filefornow)

        for item in result["results"]["bindings"]:  
            mandaatnaam = item["mandatarisUri"]["value"] #kan meer dan 1 mandataris hebben.
            Dict[name] = mandaatnaam
    return Dict


#TODO later nodig om te checeken of alle leden wel mandatrissen zijn van die bestuursorgaan
def GetAlleMandatarisVanBestuursOrgaan(bestuursOrgaan):
    sparql.setQuery("""
        PREFIX http: <http://www.w3.org/2011/http#>
        PREFIX prov: <http://www.w3.org/ns/prov#> 
        PREFIX mandaat: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX org: <http://www.w3.org/ns/org#>
        PREFIX gen: <https://data.vlaanderen.be/ns/generiek>
        PREFIX besluit: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
        PREFIX lblodlg: <http://data.lblod.info/vocabularies/leidinggevenden/>

        SELECT DISTINCT ?mandatarisUri ?naam ?achternaam 
        WHERE {
            ?bestuursorgaanPeriodUri mandaat:isTijdspecialisatieVan """ + bestuursOrgaan + """.
        
            {SELECT (max(?bindingStartDatum) AS ?RecentsteDatum)
                WHERE { 
                    ?bestuursorgaanPeriodUri mandaat:isTijdspecialisatieVan """ + bestuursOrgaan + """;
                    mandaat:bindingStart ?bindingStartDatum.
                }
            }
            ?bestuursorgaanPeriodUri mandaat:bindingStart ?RecentsteDatum.
            
            ?bestuursorgaanPeriodUri org:hasPost ?mandaatUri.
            ?mandatarisUri org:holds ?mandaatUri;
                mandaat:isBestuurlijkeAliasVan ?persoonUri .
            ?persoonUri persoon:gebruikteVoornaam ?naam ;
                foaf:familyName ?achternaam .
        } ORDER BY ?mandatarisUri

    """)
    result = sparql.query().convert()

    alleNamenBijBestuursOrgaan = []
    for item in result["results"]["bindings"]:
        eenNaam = item["naam"]["value"]
        eenAchternaam = item["achternaam"]["value"]
        volledigeNaam = eenNaam + " " + eenAchternaam 
        alleNamenBijBestuursOrgaan.append(volledigeNaam)
    return alleNamenBijBestuursOrgaan

# main()

