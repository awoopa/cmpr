import requests
import json
import nltk

from clarifai.rest import ClarifaiApp

from flask import Flask, request, jsonify
from flask.ext.cors import CORS

from htmlmin import minify

from bs4 import BeautifulSoup

from core import *

app = Flask(__name__)
CORS(app)

clarifai = ClarifaiApp(app_id='VWLdaFkl56G5o81k54s-ZI6se11adzKSFnVQ_Ggg', 
                       app_secret='QnVFC6wRIWDplb3SZBVX5iMLje_tA9oWtyj8WpcH')

clarifai_model = clarifai.models.get('general-v1.3')

@app.route('/convert_html', methods=['POST'])
def convert_html():
  """
  Given an HTML page as a string, apply all of our comprehension-improving
  transformations, and return the new HTML.
  """
  data = request.form
  html = data['page']
  return convert(html)

def convert(html):
  soup = BeautifulSoup(html, 'html.parser')
  do_things_to_html(soup, word_color)
  return minify(soup.prettify()).encode('utf-8')

def clarifai_analysis(image_url, tag_limit=10):
  """
  Given an image url return the tags as predicted by the Clarifai API.
  """
  res = clarifai_model.predict_by_url(image_url)
  return [e['name'] for e in res['outputs'][0]['data']['concepts']][:tag_limit]

def oxford_project_analysis(image_url):
  """
  Given an image url, return a description of the image as returned by the
  Oxford project API (cognitive services). Also returns tags.
  """
  json_text = {'url': image_url}
  headers = {'Ocp-Apim-Subscription-Key': '12a4c0f569884fe5b4c528b51dc890b3'}
  res = requests.post('https://api.projectoxford.ai/vision/v1.0/describe',
                       headers=headers,
                       json=json_text)

  jres = json.loads(res.text)

  return (
    jres['description']['tags'],
    jres['description']['captions'][0]['text'] if len(jres['descriptions']['captions']) else ''
  )
  
def analyze_image(image_url, tag_limit=10): 
  """
  Given an image_url and a tag_limit, make requests to both the Clarifai API
  and the Microsoft Congnitive Services API to return two things:

    (1) A list of tags, limited by tag_limit,
    (2) A description of the image
  """
  clarifai_tags = clarifai_analysis(image_url),
  ms_tags, ms_caption = oxford_project_analys(image_url)

  clarifai_tags = map(lambda s: s.lower(), clarifai_tags)
  ms_tags = map(lambda s: s.lower(), ms_tags)

  # Get tags that occur in both
  merged_tags = []
  set(ms_tags)
  for tag in clarifai_tags:
    if tag in ms_tags:
      merged_tags.append(tag)
 
  merged_tags_set = set(merged_tags)
  merged_tags += [tag for tag in clarifa_tags if tag not in merged_tags]
  merged_tags += [tag for tag in ms_tags if tag not in merged_tags]

  # Limit the tags
  merged_tags = merged_tags[:tag_limit]

  return merged_tags, ms_caption

def pos_tagging(text):
  """
  Given some text as input, return the part of speech tagging as determined by
  the Microsoft Cognitive Services API.
  """
  json_txt = {'language': 'en',
          'analyzerIds' : ["4fa79af1-f22c-408d-98bb-b7d7aeef7f04"],
          'text': text}
  headers = {'Ocp-Apim-Subscription-Key': '6728888dd73c45ada252a5f46cb0ccba'}
  res = requests.post('https://api.projectoxford.ai/linguistics/v1.0/analyze',
                       headers=headers,
                       json=json_txt)
  
  jres = json.loads(res.text)

  return jres[0]['result'][0]

def word_color(text):
  """
  Given some text as input, run part of speech tagging and return a list in the
  form:

    [('The ', 'red'), ('cat ', 'blue') ... ]
  """
  words = nltk.word_tokenize(text)
  pos_tags = pos_tagging(text)

  print(len(words))
  print(len(pos_tags))

  word_tups = []

  # last index
  li = 0

  # index into text
  i = 0

  # index into word list
  j = 0

  while i < len(text) and j < len(pos_tags):
    i += len(words[j])
    while i < len(text) and not text[i].isalpha():
      i += 1

    word_tups.append((text[li:i],
                      pos_tags[j]))
    li = i
    j += 1

  # Merge the tups if incorrectly split by tokenizer, give them a new 
  # pos tag: 'INV'
  merged_word_tups = []
  last_tup = (' ','')
  for tup in word_tups:
    if last_tup[0][-1].isalpha():
      last_tup = (
        last_tup[0] + tup[0],
        'INV'
      )
    else:
      merged_word_tups.append(last_tup)
      last_tup = tup

  merged_word_tups.append(last_tup)
  merged_word_tups = merged_word_tups[1:]

  return merged_word_tups

def main():
  print word_color("The cat in the hat likes funny memes -- I do too!")
  import pdb; pdb.set_trace()
  convert("""
CTYPE html>
<html>
<body>

<h1>My First Heading</h1>

<p>My first paragraph.</p>

</body>
</html>

  """)
  app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
  main()
