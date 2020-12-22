from sklearn.feature_extraction.text import CountVectorizer
from ....models import Country, Terroir

class WineUtils():

    def __init__(self):
        self.terroirs = Terroir.objects.all()
        super().__init__()

    def GetTerroir(self, winename, country, region):
        country_regions = list(filter(lambda c: c['country_name'] == country, terroirs))
        vocabulary = list(set([str(t['name']).lower() for t in country_regions]))
        cv = CountVectorizer(vocabulary=vocabulary, ngram_range=(1, 4))
        bag_of_words = cv.fit_transform([winename.lower() + " " + region.lower()])
        sum_words = bag_of_words.sum(axis=0) 
        words_freq = [(word, sum_words[0, idx]) for word, idx in     cv.vocabulary_.items()]
        words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
        return [w for w in words_freq if w[1] > 0]