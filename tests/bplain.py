import requests
from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request, session, url_for
from cs50 import SQL

# hardcoded url for testing
url = 'http://www.jagran.com/business/biz-gold-soars-by-990-rupee-to-31350-rupee-on-positive-global-cues-16675261.html'

# hardcoded page we are currently searching
resp = requests.get(url)

# make this a function later
# find gender
bsoup = BeautifulSoup(resp.text, "lxml")
text = bsoup.get_text()
# find the gender marker (prev_word)
#list_of_words = text.split()
# define as unicode string using 'u'
search_word = "\u0915\u0940\u092E\u0924"

list_of_words = text.split()
for i,w in enumerate(list_of_words):
    if w == search_word:
        # next word
        # print (list_of_words[i+1])
        # previous word
        if i>0:
            print (list_of_words[i-1])
