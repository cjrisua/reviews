import re, spacy, os, pprint, pandas as pd, numpy as np, requests, json, socket
from gensim.models import Word2Vec
from sklearn.decomposition import PCA
from matplotlib import pyplot
from matplotlib import pyplot as plt
from nltk.corpus import stopwords
from spacy.pipeline import EntityRuler
from spacy.tokens import Token
from spacy.matcher import Matcher
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth

class WineFingerPrint():

    def get(self,page):
        URL = f"http://{socket.gethostname()}:8000"
        try:
            response = requests.get(f"{URL}/{page}")
            response.raise_for_status()
            # access JSOn content
            return response.json()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

    def getgrapesents(self, page):
        data = []
        r = self.get(f"{page}?page=1")
        count = r["count"]
        itemsperset = len(r["results"])
        while r["next"] != None:
            data.extend(r["results"])
            r = self.get(r["next"][37:])
        data.extend(r["results"])

        grapes = [str(name['name']).lower().split() for name in data]
        grape_data = []
        for grape in grapes:
            grape_data.append( {"label": "GRP", "pattern" : grape[0] if len(grape) == 1 else [{"LOWER": g} for g in grape] })
        return grape_data

    def remove_stopwords(self,tokens):
        return [t for t in tokens if t not in  self.__stop_words]
    def convert_text(self,text):
        
        doc = self.__nlp(text)
        matches = self.__matcher(doc)
        for match_id, start, end in matches:
            string_id = self.__nlp.vocab.strings[match_id]
            span = doc[start:end]
            self.__stop_words.extend([str(span.text).lower()])
            print(f"Taster Initials: {span.text}")

        with doc.retokenize() as retokenizer:
             for ent in doc.ents:
                #retokenizer.merge(doc[3:5], attrs={"LEMMA": "new york"})
                retokenizer.merge(doc[ent.start:ent.end], attrs={"LEMMA": ent.text})
        ents = {x.text: x for x in doc.ents}
        tokens = []
        for w in doc:
            if w.is_stop or w.is_punct or w.is_digit:
                continue
            if w.text in ents:
                tokens.append(str(w.text).lower())
            else:
                tokens.append(w.lemma_.lower())

        # Remove Stop Words
        data_words_nostops = self.remove_stopwords(tokens)

        text = ' '.join(data_words_nostops)
        
        return text

    # Clean text
    def clean_text(self, text):
        # Reduce multiple spaces and newlines to only one
        text = re.sub(r'(\s\s+|\n\n+)', r'\1', text)
        # Remove double quotes
        text = re.sub(r'"', '', text)
        # Remove tester initials
        text = re.sub(r'([A-Z]{2}$)', r' \1', text)

        return self.convert_text(text)

    def __init__(self,dfwines):
        # Remove stop words and apply lemmatization
        self.__nlp = spacy.load('en_core_web_sm')
        self.__stop_words = stopwords.words('english')
        self.__stop_words.extend(['case','made'])

        self.__matcher = Matcher(self.__nlp.vocab)
        ruler = EntityRuler(self.__nlp)
        patterns = self.getgrapesents("api/varietal/")
        ruler.add_patterns(patterns)
        self.__nlp.add_pipe(ruler)
        
        pattern2 = [{"TEXT": {"REGEX": "[A-Z]{2}$"}}]
        self.__matcher.add("US", None, pattern2)

        grape_getter = lambda token: str(token.text).lower() in ("cabernet sauvignon", "petit verdot", "cabernet franc")
        Token.set_extension("is_grape", getter=grape_getter)
        
        #dfwines.type = dfwines.type.astype(int)
        train_data = dfwines[(dfwines.type == '0') | (dfwines.type =='1') ].sample(1000)
        print("train data loaded")

        list = []
        for index, rwines in train_data.groupby('terroir'):
            for index, rwine in rwines.iterrows():
                list.append([rwine.terroir,rwine.observation, rwine.type, self.clean_text(rwine.observation)])
        # Merge the list    
        reviews = pd.DataFrame(data=list, 
                        columns=["terroir", "observation", "type","clean_text"])
        #reviews = pd.concat(list)
        results = reviews.type.value_counts(normalize=True, sort=False)  
        reviews.type = reviews.type.astype(int)

        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import f1_score

        # Bag-of-words features
        bow_vectorizer = CountVectorizer(stop_words='english')
        bow = bow_vectorizer.fit_transform(reviews['clean_text'])
        df_bow = pd.DataFrame(bow.todense(), columns=bow_vectorizer.get_feature_names())

        # Splitting the data into training and test set
        X = df_bow
        y = reviews['type']

        X_train_bow, X_test_bow, y_train_bow, y_test_bow = train_test_split(X, y, test_size=0.20)

        # Fitting on Logistic Regression model
        logreg = LogisticRegression()
        logreg.fit(X_train_bow, y_train_bow)
        prediction_bow = logreg.predict_proba(X_test_bow)

        # Calculating the F1 score
        # If prediction is greater than or equal to 0.5 than 1, else 0
        # Gender, 0 = male and 1 = female
        prediction_int = prediction_bow[:,1]>=0.5
        prediction_int = prediction_int.astype(np.int)

        # Calculating F1 score
        log_bow = f1_score(y_test_bow, prediction_int)
        print(log_bow)
        
        # Import testing set
        testset = dfwines[pd.isna(dfwines.type) != False] #reviews.sample(n=100)
        # Bag-of-words feature matrix
        bow = bow_vectorizer.transform(testset['observation'])
        df_bow_test = pd.DataFrame(bow.todense(), columns=bow_vectorizer.get_feature_names())
        print(df_bow_test)

        # Predict probability
        z = df_bow_test
        pred_prob = logreg.predict_proba(z)
        pred_prob = pd.DataFrame(data=pred_prob, columns=['percentage_0', 'percentage_1'])

        # Predict classification
        pred = logreg.predict(z)
        pred = pd.DataFrame(data=pred, columns=['predicted_gender'])
        # Store into the same DataFrame
        result = pd.concat([testset, pred, pred_prob], axis=1, sort=False)

        testset.to_csv('testset.csv', encoding='utf-8')
        pred.to_csv('pred.csv', encoding='utf-8')
        pred_prob.to_csv('pred_prob.csv', encoding='utf-8')
        print("Done!")
        # 0 = male, 1 = female
        

            

        