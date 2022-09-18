from bs4 import BeautifulSoup as bs
import os
import glob
from urllib.request import urlopen
import numpy as np 
import selectQuery as sq

#-------------------------------HULPFUNTIES--------------------------------------------------------------------
def getLinksFromFile(relPathtextFiles):
    textFile = open("./"+relPathtextFiles, "r")
    links = textFile.readlines() #url's inside a text file
    return links
    
def getHtmlPageFromLink(link):
    response = urlopen(link)
    soup = bs(response, 'html.parser')
    return soup

def GetHtmlPageFromListOfLinks(LinkOfLinks):
    listOfHtmls = []
    for Link in LinkOfLinks:
        listOfHtmls.append(getHtmlPageFromLink(Link))
    return listOfHtmls

def getTagsFromProperty(html):
    Tags0 = html.find_all(property="besluit:heeftAanwezigeBijStart") 
    Tags1 = html.find_all(property="besluit:heeftSecretaris besluit:heeftAanwezigeBijStart") 
    Tags2 = html.find_all(property="besluit:heeftVoorzitter besluit:heeftAanwezigeBijStart") 
    Tags = Tags0 + Tags1 + Tags2
    return Tags

def getTagsFromPropertyFromList(HtmlList):
    ListOfHtmlsOfTags = []
    for HtmlPage in HtmlList:
        ListOfHtmlsOfTags.append(getTagsFromProperty(HtmlPage))
    return ListOfHtmlsOfTags

def getTextFromInsideTag(tag):
    Persoonsnaam = tag.getText() 
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
    
def getListOfTextFromInsideListOfTags(listOfTagsOfLinks):
    Personen = []
    for Link in listOfTagsOfLinks:
        Personen.append(getTextFromList(Link))
    return Personen

#gegeven naam, geef mandatarisUri terug in een dictionary
def getDictOfMandaFromListName(ListOfNames):
    Dict = {}
    for Person in ListOfNames:
        Dict[Person]=sq.GetMandatarissenPerson(Person)
    return Dict

#-------------- Geef Alle Namen Te vinden op de text file met links gegeven. ----------------------------

def getNamesFromWebPage(): 
    textFiles = [os.path.basename(x) for x in glob.glob('./*.txt')]
    if (len(textFiles)>1):
        raise Exception("Too Many Text Files In Folder , More than 1 txt file in folder")
    else:
        nestedListOfLinks = getLinksFromFile(textFiles[0]) 
        listOfHtmls = GetHtmlPageFromListOfLinks(nestedListOfLinks)
        listOfTags = getTagsFromPropertyFromList(listOfHtmls) 
        nestedListOfText = getListOfTextFromInsideListOfTags(listOfTags)
    return nestedListOfText

def getNamesFromSittingFromDatabase(linkToSittings):
    return sq.GetAllAanwezigeQuery(linkToSittings)

#-------------- Geef alle namen die ontbreken in de centrale vindplaats van de gegeven links en hun corresponderende zittingUri ------------------
def wieOntrbreekt():
    NestedlijstVNamen = getNamesFromWebPage() #aanwezigen volgens html pagina(correct)
    lijstVPersonen = getNamesFromSittingFromDatabase() #aanweizgenbijstart volgens centrale vindplaats
    
    #TODO check als ze leden zijn van die bestuursorgaan.
         
    #vergelijken
    ontbrekendePersonenPerLink = []
    for i in range(NestedlijstVNamen):
        if(len(NestedlijstVNamen[i]) != len(lijstVPersonen)):
            print("Er is een discrepantie")
            temp = [x for x in NestedlijstVNamen[i] if x not in lijstVPersonen] 
            #hoeft niet omgekeerde richting checken, sinds we aannemen dat html correct is. 
            # dus we nemen aan dat [x for x in lijstVPersonen if x not in lijstVNamen] een lege lijst is
        else:
            print("Er is geen discrepantie")
            temp = []
        ontbrekendePersonenPerLink.append(getDictOfMandaFromListName(temp))
    return ontbrekendePersonenPerLink  

def main():
    Names = wieOntrbreekt()




































