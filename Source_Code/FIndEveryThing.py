from ast import Not
from bs4 import BeautifulSoup as bs
import os
import glob
from urllib.request import urlopen
import numpy as np 
import selectQuery as sq
import time as t
import json 
import matplotlib.pyplot as plt
#------------------------------------------------------------------------------------
#------------------------------- HULPFUNTIES ----------------------------------------
#------------------------------------------------------------------------------------

# def getLinksFromFile(relPathtextFiles):
#     textFile = open("./"+relPathtextFiles, "r")
#     links = textFile.readlines() #url's inside a text file
#     return links
    
def getHtmlPageFromLink(link):
    response = urlopen(link)
    soup = bs(response, 'html.parser')
    return soup

# def GetHtmlPageFromListOfLinks(LinkOfLinks):
#     listOfHtmls = []
#     for Link in LinkOfLinks:
#         listOfHtmls.append(getHtmlPageFromLink(Link))
#     return listOfHtmls

def getTagsFromProperty(html):
    Tags0 = html.find_all(property="besluit:heeftAanwezigeBijStart") 
    Tags1 = html.find_all(property="besluit:heeftSecretaris besluit:heeftAanwezigeBijStart") 
    Tags2 = html.find_all(property="besluit:heeftVoorzitter besluit:heeftAanwezigeBijStart") 
    Tags = list(set(Tags0 + Tags1 + Tags2))
    return Tags

# def getTagsFromPropertyFromList(HtmlList):
#     ListOfHtmlsOfTags = []
#     for HtmlPage in HtmlList:
#         ListOfHtmlsOfTags.append(getTagsFromProperty(HtmlPage))
#     return ListOfHtmlsOfTags

def getTextFromInsideTag(tag):
    Persoonsnaam = tag.getText() 

    #TODO PROBLEEM: nameparser? -> zeer lastig uit de string zelf. 
    # Oplossing: mandatendatabank, voornaam en achternaam met spatie aan elkaar zetten = 'mandaatnaam'
    # kijken of 'persoonsnaam' in (contains) 'mandaatnaam' voor een gedeelte voorkomt, 
    # Als zo voorkomt, gebruik dan 'mandaatnaam' als 'persoonsnaam' 

    #TODO ipv string terug te geven, geef lijst terug [voornaam, achternaam]

    Persoonsnaam = Persoonsnaam.strip() # delete all \n from string
    return Persoonsnaam

def getTextFromList(listOfTags):
    mensen = []
    AantalAanwezige = len(listOfTags)
    if(AantalAanwezige>=1):
        for Tag in listOfTags:
            TagText = getTextFromInsideTag(Tag)
            mensen.append(TagText)
    else:
        pass
    return mensen

def getElementOfListInAList(NestedListOfLinksAndBestuursOrganen,FirstOrSecondElement):
    ListOfOnlyLinks = []
    for LISTO in NestedListOfLinksAndBestuursOrganen:
        ListOfOnlyLinks.append(LISTO[FirstOrSecondElement])
    return ListOfOnlyLinks
    
# def getListOfTextFromInsideListOfTags(listOfTagsOfLinks):
#     Personen = []
#     for Link in listOfTagsOfLinks:
#         Personen.append(getTextFromList(Link))
#     return Personen

#gegeven naam, geef mandatarisUri terug in een dictionary
def getDictOfMandaFromListName(ListOfNames,zittingUri,everthinh):
    return sq.GetMandatarissenPerson(ListOfNames,zittingUri,everthinh)


#------------------------------------------------------------------------------------
#-------------------------------- 3 GROTE ONDERDELEN --------------------------------
#------------------------------------------------------------------------------------

def getNamesFromWebPage(Everything): 
    LISTO = {}
    for sitting in list(Everything.keys()):
        link = Everything[sitting][0]
        soup = getHtmlPageFromLink(link)
        tags = getTagsFromProperty(soup)
        text = getTextFromList(tags)
        LISTO[sitting] = text
        # listOfHtmls = GetHtmlPageFromListOfLinks(nestedListOfLinks)
        # listOfTags = getTagsFromPropertyFromList(listOfHtmls) 
        # nestedListOfText = getListOfTextFromInsideListOfTags(listOfTags)
    return LISTO

def getNamesFromSittingFromDatabase(Everything):
    dict={}
    for sitting in list(Everything.keys()):
        dict[sitting] = sq.GetAllAanwezigeQuery(sitting)
    return dict

def Comparing(NestedLijstVanNamenVanHtml, NestedLijstVanNamenVanDatabase, Everything):
    for sitting in list(Everything.keys()):
        temp = []
        if(len(NestedLijstVanNamenVanHtml[sitting]) != len(NestedLijstVanNamenVanDatabase[sitting])):
            temp = [x for x in NestedLijstVanNamenVanHtml[sitting] if x not in NestedLijstVanNamenVanDatabase[sitting]] 
            #hoeft niet omgekeerde richting checken, sinds we aannemen dat html correct is. 
            # dus we nemen aan dat [x for x in lijstVPersonen if x not in lijstVNamen] een lege lijst is
            ontbrekendePersonen = getDictOfMandaFromListName(temp,sitting,Everything)
            Everything[sitting][2] = ontbrekendePersonen

    return Everything


#------------------------------------------------------------------------------------
#--------------------------------- MAIN FUNCTIONS -----------------------------------
#------------------------------------------------------------------------------------

def wieOntrbreekt(aantalZittingen, time=False):
    A1 = t.time() #stap 1
    Everything = sq.getAllSittingsFromEveryBestuursEenheid(aantalZittingen)
    #aanwezigen volgens html pagina(we nemen aan dat dit altijd correct ingevuld is)
    A2 = t.time() #stap 2 
    #TODO getNamesFromWebPage efficienter maken. 
    LijstVanNamenVanHtml = getNamesFromWebPage(Everything) 
    #aanwezigen volgens zitting in database, centrale vindplaats
    A3 = t.time() #stap 3 
    LijstVanNamenVanDatabase = getNamesFromSittingFromDatabase(Everything) 

    A4 = t.time() #stap 4 
    #TODO check als ze leden zijn van bijhorende bestuursorgaan.
    #TODO check bij zitting dat meer dan de helft van de leden van de bestuursorgaan aanwezig zijn. 
    #TODO comparing Efficienter maken.
    RESULT = Comparing(LijstVanNamenVanHtml,LijstVanNamenVanDatabase,Everything)
    A5 = t.time()


    if not time:
        return RESULT
    else : 
        return [A2-A1,A3-A2,A4-A3,A5-A4]

def main(aantalzittingen, time=False):
    begin = t.time()
    if not time :
        Names = wieOntrbreekt(aantalzittingen)
        with open("sample" + str(aantalzittingen) + ".json", "w") as outfile:
            json.dump(Names, outfile)
        return Names
    else: 
        Time = wieOntrbreekt(aantalzittingen,True)
        eind = t.time()
        TOTAAL_TIJD =  eind-begin
        return Time + [TOTAAL_TIJD]
    

def AnalyzeTiming(x,y):
    lijst = []
    dict = {}
    dict["lijst1"] = [] 
    dict["lijst2"] = [] 
    dict["lijst3"] = [] 
    dict["lijst4"] = [] 
    dict["lijst5"] = [] 
    x = np.array(range(0, x, y))
    for i in x:
        print("Aantalzittingen: ", i)
        tijd = main(i)
        dict["lijst1"].append(tijd[0]) # tijd voor stap 1 voor i aantal zittingen
        dict["lijst2"].append(tijd[1]) # stap 2
        dict["lijst3"].append(tijd[2]) # stap 3
        dict["lijst4"].append(tijd[3]) # stap 4 
        dict["lijst5"].append(tijd[4]) # alles samen = stap 5 = stap 1 + stap 2 + ... + stap 4
        lijst.append(tijd)
    
    print(lijst)
    for i in range(5):
        y = np.array(dict["lijst" + str(i+1)])
        # plot
        print(x)
        print(y)
        plt.plot(x,y)
        plt.xlabel('Aantal Zittingen')
        plt.ylabel('Tijd (in seconden)')
        plt.legend("Stap" + str(i+1))
        plt.savefig("Stap" + str(i+1) + ".png")
        plt.show()
    
    
    return 0

main(1)
# AnalyzeTiming(100,10)