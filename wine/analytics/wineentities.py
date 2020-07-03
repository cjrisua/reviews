from __future__ import unicode_literals, print_function
import plac
import random
import warnings
import spacy
from spacy.util import minibatch, compounding
from pathlib import Path

class WineEntities():

    def __init__(self):
        super().__init__()
        self.__nlp = spacy.load("./model")  # load existing spaCy model
    def ReadEntities(self, text):
        doc = self.__nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
    
