from django.test import TestCase

# Create your tests here.
import requests
from bs4 import BeautifulSoup

# hardcoded page we are currently searching
resp = requests.get('http://www.jagran.com/business/biz-gold-soars-by-990-rupee-to-31350-rupee-on-positive-global-cues-16675261.html?src=p2')

bsoup = BeautifulSoup(resp.text, "lxml")
#text = bsoup.get_text()

text = ''
# get only <p> tags
for para in bsoup.find_all('p'):
    text = text + para.text + '\n'

print(text.encode('utf8'))

# define as unicode string using 'u'
search_word = "\u0915\u0940\u092E\u0924"

# print out the previous word for each occurance of target
list_of_words = text.split()
for i,w in enumerate(list_of_words):
    if w == search_word:
        # next word
        # print (list_of_words[i+1])
        # previous word
        if i>0:
            print (list_of_words[i-1].encode('utf8'))
