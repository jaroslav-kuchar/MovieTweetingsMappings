# MovieTweetingsMappings
Mappings of movies from [MovieTweetings](https://github.com/sidooms/MovieTweetings) (published by [Simon Dooms](https://github.com/sidooms/MovieTweetings)) to DBpedia. 

If you publish research that uses MovieTweetingsMappings, please cite:
```bib
@inproceedings{Kuchar:2015:MovieTweetingsMappings,
  author    = {Jaroslav Kuchar},
  title     = {Augmenting a Feature Set of Movies Using Linked Open Data},
  booktitle = {Joint Proceedings of the 9th International Rule Challenge, Challenge on Rule-based Recommender Systems for the Web of Data, RuleML2015 Industry Track and and the 5th RuleML Doctoral Consortium 2015, Berlin, Germany, August 2-5, 2015.},
  year      = {2015}
}
```

## Format
CSV file, records separated by semicolon (**;**)
* id - id of movie in MovieTweetings
* title - title (year)
* genre - assigned genres
* uri - DBpedia URI
* method - method of mapping (perfect|partial|pattern|any)
* tc - title confidence
* yc - year confidence
* gc - genre confidence
* updated - datetime of last update

## Example
id | title | genre | uri | method | tc | yc | gc | updated
--- | --- | --- | --- | --- | --- | --- | --- | --- 
75148 | Rocky (1976) | Drama\|Sport | http://dbpedia.org/resource/Rocky | perfect | 1.0 | 1.0 | 1.0 |2015-06-01T11:33:06

## Confidence Values
### Title Confidence
<img src="./docs/tc.png?raw=true" height="20" />
### Year Confidence
<img src="./docs/yc.png?raw=true" height="20" />
### Genre Confidence
<img src="./docs/gc.png?raw=true" height="40" />

## Methods
* perfect - perfect match of title and year (e.g. Rocky, Rocky (film), Rocky (1976 film), etc.)
* partial - partial match of title and year
* pattern - pattern-based match of abstract (e.g. Rocky is a ... 1976 ..., Rocky ... released 1976 ..., etc)
* any - any partail match in asbtract (... also known as ..., German: ..., etc. )

## Contributors
- Jaroslav Kuchař (https://github.com/jaroslav-kuchar)
