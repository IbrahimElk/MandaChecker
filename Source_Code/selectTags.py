from logging import exception
from bs4 import BeautifulSoup as bs
import os
import glob
from urllib.request import urlopen
import numpy as np 

def main():
    getNames()

def getNames():
    #-----------Get Links from file
    textFiles = [os.path.basename(x) for x in glob.glob('./*.txt')]
    if (len(textFiles)>1):
        exception("Too Many Text Files In Folder , More than 1 txt file in folder")
    else : 
    Files = []
    for textFile in textFiles :
        my_file = open(textFile, "r")
        links = my_file.readlines() #url's inside a text file
        print("pls", links)
    #-----------Dowlaod html from link
        counter = 0
        Links = []
        for url in links:
            #print(url)
            response = urlopen(url)
            soup = bs(response, 'html.parser')
        # ---------- Get all names in any tag with certain property
            Tags0 = soup.find_all(property="besluit:heeftAanwezigeBijStart") 
            Tags1 = soup.find_all(property="besluit:heeftSecretaris besluit:heeftAanwezigeBijStart") #??? 
            #Tags2 = soup.find_all(property="besluit:heeftVoorzitter besluit:heeftAanwezigeBijStart") #??? 
            AantalAanwezige = len(Tags0) + len(Tags1)
            
            if(AantalAanwezige>=1):
                Personen = []
                for i in range(0,len(Tags0)):
                    Persoonsnaam = Tags0[i].getText() 
                    Persoonsnaam = Persoonsnaam.strip() # delete all \n from string
                    Personen.append(Persoonsnaam)
                for i in range(0,len(Tags1)):
                    Persoonsnaam = Tags1[i].getText() 
                    Persoonsnaam = Persoonsnaam.strip() # delete all \n from string
                    Personen.append(Persoonsnaam)
            else:
                #print("No tags found in this Url: " + url)
                pass
        Links.append(Personen)
    Files.append(Links)
    return Files

main()
