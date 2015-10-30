import urllib
import urllib2
import json
import re
import enchant
import sys
import csv


url = 'http://en.wikipedia.org/w/api.php'  ## url link to wiki's API 
validWord = True # Optional, check whether found words are valid words in English. Change it to False if not desired.

## Get the wiki titles from the links given by the user
## Wikipedia pages titles are always after the last '/', for now at least
def getTitles(input_list):

	titles_list = map(lambda x: x[x.rfind('/')+1 : ], input_list)  

	return titles_list

## Get the pageid for a certain wiki page, in order to access the content
def getPageID(wikijson):
	
	key = re.sub('[^0-9]+','',str(wikijson['query']['pages'].keys()))
	
	return str(key)

# Get the wikipage content
# answers to question a) and b)
def getWiki(title):

	values = {'action' : 'query',
	          'prop' : 'revisions',
	          'titles' : title,
	          'rvprop' : 'content',
	          'format' : 'json'}
	try: 
		data = urllib.urlencode(values)
		req = urllib2.Request(url, data)
		response = urllib2.urlopen(req)
		jsonfile = json.loads(response.read())
	except:
		print 'Codes might not work any more, please consult Peiyun Zhu'
	
	try:
		content = str(jsonfile['query']['pages'][getPageID(jsonfile)]['revisions'])
	except:
		print 'Title is not valid. Further investigation is needed'

	content_clean = re.sub('[^a-zA-Z]+',' ',content).lower().split(' ')  	# remove all special characters and numbers
	content_clean_filter = filter(lambda x : len(x) > 1 , content_clean)	# remove single letters as they cannot have different anagram than themselves
	
	# PyEnchant is a python package that check whether a word is valid in English
	# Words like 'www' or 'http' will be removed
	d = enchant.Dict("en_US")
	if validWord == True:
		content_clean_filter = filter(lambda x : d.check(x) == True , content_clean_filter)

	return list(content_clean_filter)

# Given a list of words, check anagrams using dictionary (Hash table)
# answers to question c)
def anagrams(strs):

    records = {}

    for string in strs:
        letters = list(string)
        keys = "".join(sorted(letters))
        bucket = records.get(keys, [])
        bucket.append(string)
        records[keys] = bucket
    result = []

    for bucket in records.values():
        if len(bucket)>1:
            result.append(bucket)  

    return result

# the main function
def main(wikiInput=None,outputfile='output.csv'):

	if len(sys.argv) < 2:
		print 'Please give us a wikipedia link!'
		raise ValueError('No link is given')

	wikiInput = sys.argv[1]

	if len(sys.argv) == 3:
		outputfile = sys.argv[2]

	input_list = wikiInput.split('||')

	# check non-wiki input
	for input in input_list:
		if input.find('wikipedia.org/wiki/') == -1:
			print 'FAIL! Please enter a valid wikipedia link'
			print 'A good example: https://en.wikipedia.org/wiki/Barack_Obama'
			raise ValueError('A bad link is given:', input)

	# decode some potential url encoding in the links
	input_list = map(lambda x: urllib.unquote(x).decode('utf8'),input_list)  

	titles_list = getTitles(input_list)

	list_of_words = []

	# Combine content from all links
	for i in range(len(titles_list)):
		list_of_words += getWiki(titles_list[i])

	# Dedup on the words
	# For example, list = ['peiyun','zhu','zhu']. Double 'zhu' in the list doesn't give us any benefit and will slow down the program
	list_of_words_deduped = list(set(list_of_words))

	results_ana = anagrams(list_of_words_deduped)

	# Open File
	resultFile = open(outputfile,'wb')

	# Create Writer Object
	wr = csv.writer(resultFile, dialect='excel')

	# Write Data to File
	wr.writerows(results_ana)

if __name__ == "__main__":
	main()
