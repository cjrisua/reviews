from bs4 import BeautifulSoup
from enum import Enum
import re
class WineRegion():
    @property
    def parent(self):
        return self.__subregion
    @property
    def subregion(self):
        return self.__subregion
    @subregion.setter
    def subregion(self,region):
        self.__subregion = region

    def __init__(self,parent,name):
        self.__name = name
        self.__parentregion = parent
        self.__subregion = None
        
class Region(WineRegion):
    
    def __init__(self, name, country):
        self.__country = country
        super().__init__(None,name)

class Size(Enum):
    Empty = 0
    ml750 = 1
    ml375 = 2
    L1half = 3


class Bottle():
    @property
    def price(self):
        return self.__price
    @property
    def size(self):
        return self.__size

    def __init__(self, size,price):
        if size == '(750ml)':
            self.__size = Size.ml750
        elif size == '(375ml)':
            self.__size = Size.ml375
        elif size == '(1.5L)':
            self.__size = Size.L1half
        else:
            self.__size = Size.Empty

        self.__price = price

class Wine():
    @property
    def score(self):
        return self.__score
    @score.setter
    def score(self,value):
        self.__score = value
    @property
    def bottle(self):
        return self.__bottle
    @bottle.setter
    def bottle(self,value):
        self.__bottle.append(value)
    @property
    def region(self):
        return self.__region
    @property
    def location(self):
        return self.__location
    @location.setter
    def location(self,value):
        region = None
        locationlist = str(value).split(">")
        for i,name in enumerate(locationlist[1:],1):
            if i == 1:
                region = Region(locationlist[0].strip(" "),name.strip(" "))
            else:
                subregion = WineRegion(region, name.strip(" ").strip("\n"))
                region.SubRegion = subregion
                region = region.SubRegion

        while region._WineRegion__parentregion is not None:
            region = region._WineRegion__parentregion
        self.__region = region
        self.__location = value

    @property
    def name(self):
        return self.__name
    @name.setter
    def name(self,val):
        self.__name = val
        if len(re.match("^([0-9]+)\s", val).groups()) > 0:
            self.__vintage = re.match("^([0-9]+)\s", val).groups()[0]
            self.__name = str(self.__name).replace(self.__vintage,"").strip(" ")
        else:
            self.__vintage = "NBV"       
    @property
    def type(self):
        return self.__type
    @type.setter
    def type(self,val):
        self.__type = val
    @property
    def id(self):
        return self.__id

    def __str__(self):
        return self.__name + f" [{len(self.__bottle)}]"

    def __init__(self, id):
        self.__vintage = "None"
        self.__type = "None"
        self.__name = "None"
        self.__country = "None"
        self.__region = "None"
        self.__location  = "None"
        self.__bottle = []
        self.__score = "None"
        self.__id = id

with open("CellarTracker_MyWines.htm","r", encoding="utf-8") as f:
    winecollection = []
    contents = f.read()
    soup = BeautifulSoup(contents, features="html.parser")
    for element in soup.find_all("tr"):

        iWine = element.find_all("input", {"name":"iWine"})
        if len(iWine) == 0:
            continue
        wine = Wine(iWine[0].attrs['value'])
        if wine.id == "1605012":
            print("H")
        try:
            for data in element.find_all("td"):
                if 'type' in data.attrs["class"]:
                    wine.type = data.a.contents[0]
                elif 'name' in data.attrs["class"]:
                    wine.name = data.find("span", class_='nam').h3.contents[0]
                    wine.location = data.find("span", class_='loc').contents[0]
                elif 'dates' in data.attrs["class"]:
                    for b in data.find_all("span", class_='qtv'):
                        bottle = Bottle([em for em in b.find_all("em") if em.string != "+"][0].string,
                                        b.find("span", class_='val').span.contents)
                        for w in range(int(max([i for i in b.find("span", class_='num').contents if str(i).isdigit()]))):
                            wine.bottle = bottle

                    #wine.bottle = [bottle] * 
                elif 'score' in data.attrs["class"]:
                    if len([a for a in data.children if a.name == 'a']) > 0:
                        wine.score = data.find("span", class_='scr').a.contents[0]
            if len(wine.id) != "0":
                print(f"{wine.id}@{wine.name}@{len(wine.bottle)}")
            winecollection.append(wine)
        except:
            print(f"Error processing {wine}")

    print(sum([len(w.bottle) for w in winecollection]))