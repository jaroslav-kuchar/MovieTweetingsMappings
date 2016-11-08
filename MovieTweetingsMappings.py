
# coding: utf-8

# In[1]:

"""
Import modules
"""
import urllib
import zipfile
import pandas as pd
import numpy as np
import warnings
import rdflib
import re
from SPARQLWrapper import SPARQLWrapper, JSON
import random
import datetime
warnings.filterwarnings('ignore')
sparqlEndpoint = "http://dbpedia.org/sparql"
# sparqlEndpoint = "http://live.dbpedia.org/sparql"


# In[2]:

"""
Levenshtein distance
"""
# http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
def levenshtein(source, target):
    if len(source) < len(target):
        return levenshtein(target, source)
 
    # So now we have len(source) >= len(target).
    if len(target) == 0:
        return len(source)
 
    # We call tuple() to force strings to be used as sequences
    # ('c', 'a', 't', 's') - numpy uses them as values by default.
    source = np.array(tuple(source))
    target = np.array(tuple(target))
 
    # We use a dynamic programming algorithm, but with the
    # added optimization that we only need the last two rows
    # of the matrix.
    previous_row = np.arange(target.size + 1)
    for s in source:
        # Insertion (target grows longer than source):
        current_row = previous_row + 1
 
        # Substitution or matching:
        # Target and source items are aligned, and either
        # are different (cost of 1), or are the same (cost of 0).
        current_row[1:] = np.minimum(
                current_row[1:],
                np.add(previous_row[:-1], target != s))
 
        # Deletion (target grows shorter than source):
        current_row[1:] = np.minimum(
                current_row[1:],
                current_row[0:-1] + 1)
 
        previous_row = current_row
 
    return previous_row[-1]

def levenshteinTile(original, year, dbpedia):
#     original = original.decode('utf-8')
    return min([levenshtein(original+"",dbpedia), levenshtein(original+" (film)",dbpedia), levenshtein(original+" ("+year+" film)",dbpedia)])


# In[3]:

def categoryMatch(uri, categories):
    if uri is None or len(categories)==0:
        return 0.0
    sparql = SPARQLWrapper(sparqlEndpoint)
    query = """
    SELECT DISTINCT ?category WHERE {
        <%s> dct:subject ?cat .
        ?cat rdfs:label ?category .
        }
    """ % (uri)
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    if len(results["results"]["bindings"])>0:
        return sum([max([re.search(cat, dbcat["category"]["value"], re.IGNORECASE) is not None for dbcat in results["results"]["bindings"]]) for cat in categories])/float(len(categories))
    else:
        return 0.0


# In[4]:

def checkExactNameYear(name, year):
    sparql = SPARQLWrapper(sparqlEndpoint)
    query = """
        SELECT DISTINCT ?movie ?title ?cat WHERE {
            ?movie rdf:type dbo:Film ;
            rdfs:label ?title .
            ?movie dct:subject ?cat .
            ?cat rdfs:label ?year .
            FILTER (((str(?title)="%s" || str(?title)="%s (film)") && regex(?year,"^%s film", "i")) || str(?title)="%s (%s film)")
        }
        ORDER BY ASC(?movie) 
    """ % (name, name, year, name, year)
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    uris = [(result["movie"]["value"]).encode("utf-8") for result in results["results"]["bindings"]]  
    uris = list(set(uris))
    if len(uris)==1:
        confidence = min([levenshteinTile(name, year, result["title"]["value"]) for result in results["results"]["bindings"]])
        confidence = 1.0-confidence/float(len(name))
        return str(uris[0]), confidence
    else: 
        return None, 0.0


# In[5]:

def checkRegexpNameYear(name, year):
    sparql = SPARQLWrapper(sparqlEndpoint)
    query = """
        SELECT DISTINCT ?movie ?title ?cat WHERE {
            ?movie rdf:type dbo:Film ;
            rdfs:label ?title .
            ?movie dct:subject ?cat .
            ?cat rdfs:label ?year .
            FILTER regex(?title,"%s", "i") .
            FILTER regex(?year,"%s", "i")
        }
        ORDER BY ASC(?movie) 
    """ % (name,year)
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    uris = [(result["movie"]["value"]).encode("utf-8") for result in results["results"]["bindings"]]  
    uris = list(set(uris))
    if len(uris)==1:
        confidence = min([levenshteinTile(name, year, result["title"]["value"]) for result in results["results"]["bindings"]])
        confidence = 1.0-confidence/float(len(name))
        return str(uris[0]), confidence
    else: 
        return None, 0.0


# In[6]:

def checkIsAAbstractYear(name, year):
    sparql = SPARQLWrapper(sparqlEndpoint)
    query = """
        SELECT DISTINCT ?movie ?title ?abstract ?cat WHERE {
            ?movie rdf:type dbo:Film ;
            dbo:abstract ?abstract;
            rdfs:label ?title .
            FILTER (regex(?abstract,"^%s is a %s", "i") || regex(?abstract,"^%s .* releas.* %s", "i"))
        }
        ORDER BY ASC(?movie) 
    """ % (name, year, name, year)
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    uris = [(result["movie"]["value"]).encode("utf-8") for result in results["results"]["bindings"]]  
    uris = list(set(uris))
    if len(uris)==1:
        confidence = min([levenshteinTile(name, year, result["title"]["value"]) for result in results["results"]["bindings"]])
        confidence = 1.0-confidence/float(len(name))
        return str(uris[0]), confidence
    else: 
        return None, 0.0


# In[7]:

def checkRegexpAbstractYear(name, year):
    sparql = SPARQLWrapper(sparqlEndpoint)
    query = """
        SELECT DISTINCT ?movie ?title ?abstract ?cat WHERE {
            ?movie rdf:type dbo:Film ;
            dbo:abstract ?abstract;
            rdfs:label ?title .
            ?movie dct:subject ?cat .
            ?cat rdfs:label ?year .
            FILTER regex(?abstract,"%s", "i").
            FILTER regex(?year,"%s", "i")
        }
        ORDER BY ASC(?movie) 
    """ % (name,year)
    sparql.setQuery(query)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    uris = [(result["movie"]["value"]).encode("utf-8") for result in results["results"]["bindings"]]  
    uris = list(set(uris))
    if len(uris)==1:
        confidence = min([levenshteinTile(name, year, result["title"]["value"]) for result in results["results"]["bindings"]])
        confidence = 1.0-confidence/float(len(name))
        return str(uris[0]), confidence
    else: 
        return None, 0.0


# In[8]:

def getMapping(title, year, categories):
    # same title and year
    uri, confidence = checkExactNameYear(title, year)
    if uri is not None:
        return uri, confidence, "perfect"
    uri, confidence = checkIsAAbstractYear(title, year)
    if uri is not None:
        return uri, confidence, "pattern"
    uri, confidence = checkRegexpNameYear(title, year)
    if uri is not None:
        return uri, confidence, "partial"
    uri, confidence = checkRegexpAbstractYear(title, year)
    if uri is not None:
        return uri, confidence, "any"
    
    # same title, year+1
    uri, confidence = checkExactNameYear(title, str(int(year)+1))
    if uri is not None:
        return uri, confidence, "perfect"
    uri, confidence = checkIsAAbstractYear(title, str(int(year)+1))
    if uri is not None:
        return uri, confidence, "pattern"
    uri, confidence = checkRegexpNameYear(title, str(int(year)+1))
    if uri is not None:
        return uri, confidence, "partial"
    uri, confidence = checkRegexpAbstractYear(title, str(int(year)+1))
    if uri is not None:
        return uri, confidence, "any"
    
    # same title, year-1
    uri, confidence = checkExactNameYear(title, str(int(year)-1))
    if uri is not None:
        return uri, confidence, "perfect"
    uri, confidence = checkIsAAbstractYear(title, str(int(year)-1))
    if uri is not None:
        return uri, confidence, "pattern"
    uri, confidence = checkRegexpNameYear(title, str(int(year)-1))
    if uri is not None:
        return uri, confidence, "partial"
    uri, confidence = checkRegexpAbstractYear(title, str(int(year)-1))
    if uri is not None:
        return uri, confidence, "any"   
    
    return None, 0.0, ""
    


# In[9]:

"""
Download
"""
retriveResult = urllib.urlretrieve("https://raw.githubusercontent.com/sidooms/MovieTweetings/master/latest/movies.dat", "./latest-movies.dat")


# In[10]:

"""
Read data
"""
movies = pd.read_csv("./latest-movies.dat", sep="::", encoding="utf-8", header=None, names=["id", "title", "genre"])
latestMappings = pd.read_csv("./mappings.csv", sep=";", encoding="utf-8")


# In[11]:

"""
Print Details 
"""
print "MovieTweetings movies: {0}".format(movies.shape)
print movies[:3]
print "Mappings: {0}".format(latestMappings.shape) 
print latestMappings[:3]


# In[ ]:

"""
Merge
"""
print "Movies {} + Latest mappings {}".format(movies.shape, latestMappings.shape)
mappings = pd.merge(movies, latestMappings, on="id", how="left")
mappings.drop(["title_y", "genre_y"], axis=1, inplace=True)
mappings.rename(columns={"title_x":"title", "genre_x":"genre"}, inplace=True)
print "Mappings Merged: {} \n ...".format(mappings.shape)
print mappings[:3]
mappings.to_csv("./mappings.csv", index=False, sep=";", encoding="utf-8")        


# In[ ]:

mappings = pd.read_csv("./mappings.csv", sep=";", encoding="utf-8")
mappings.fillna("")

toUpdate = np.random.choice(mappings.sort(["updated"]).head(20000).index.values,100)

for id, row in mappings.iterrows():
    if str(row["updated"]) == "nan" or id in toUpdate:
        originalTitle = row["title"]
        originalCategories = row["genre"]
        name = originalTitle[0:originalTitle.rfind(" ")].replace("?","")
        year = originalTitle[originalTitle.rfind(" ")+1:].replace("(","").replace(")","")
        categories = originalCategories.split("|") if type(originalCategories) is str or type(originalCategories) is unicode else []
        name = name.strip()
        year = year.strip()
        print "{0}: {1}, {2}, {3}".format(id, name.encode("utf-8"), year, categories)

        uri, titleConfidence, method = getMapping(name, year, categories)
        categoryConfidence = categoryMatch(uri, categories)
        yearConfidence = 0.0
        if uri is not None:
            yearConfidence = 1.0
            if method.endswith("-") or method.endswith("+"):
                yearConfidence = 1.0-1.0/float(year)
        print "URI: {0}".format(uri)
        print "Method: {0}".format(method)
        print "Title confidence: {0}".format(titleConfidence)
        print "Year confidence: {0}".format(yearConfidence)
        print "Categories confidence: {0}".format(categoryConfidence)
        
        if titleConfidence > 0.0:
            print "--> mapped"
            mappings.iloc[id,3] = uri
            mappings.iloc[id,4] = method
            mappings.iloc[id,5] = titleConfidence
            mappings.iloc[id,6] = yearConfidence
            mappings.iloc[id,7] = categoryConfidence
        else:
            print "--> unmapped"
            mappings.iloc[id,3] = None
            mappings.iloc[id,4] = None
            mappings.iloc[id,5] = 0.0
            mappings.iloc[id,6] = 0.0
            mappings.iloc[id,7] = 0.0
        
        print "\n"    
        mappings.iloc[id,8] = str(datetime.datetime.now().replace(microsecond=0).isoformat())
        mappings.to_csv("./mappings.csv", index=False, sep=";", encoding="utf-8")        

