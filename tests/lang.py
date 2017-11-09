from langdetect import detect # googles language detect library

# define as unicode string using 'u'
search_word = "\u0915\u0940\u092E\u0924"

# check if its Hindi
result = detect(search_word)

print (result)