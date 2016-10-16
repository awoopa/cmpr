import requests
import json
import nltk
import math

from rapidconnect import RapidConnect

from clarifai.rest import ClarifaiApp

from flask import Flask, request, jsonify
from flask.ext.cors import CORS

from htmlmin import minify

from bs4 import BeautifulSoup

from core import *

from nltk.tag.perceptron import PerceptronTagger

from nltk.corpus import brown

from nltk import tokenize

import numpy as np

from scipy.sparse import csc_matrix

app = Flask(__name__)
CORS(app)

clarifai = ClarifaiApp(app_id='VWLdaFkl56G5o81k54s-ZI6se11adzKSFnVQ_Ggg', 
                       app_secret='QnVFC6wRIWDplb3SZBVX5iMLje_tA9oWtyj8WpcH')

clarifai_model = clarifai.models.get('general-v1.3')

tagger = PerceptronTagger()

total_word_counts = {}

for s in brown.sents():
  s = map(lambda k: k.lower(), s)
  for w in set(s):
    if w not in total_word_counts:
      total_word_counts[w] = 0
    total_word_counts[w] += 1

brown_sent_count = len(brown.sents())
rapid = RapidConnect('cmpre', 'a0c4b418-1531-4c31-abbe-24df50f8a74b');

@app.route('/convert_html', methods=['POST'])
def convert_html():
  """
  Given an HTML page as a string, apply all of our comprehension-improving
  transformations, and return the new HTML.
  """
  data = request.get_json(force=True)
  html = data['page']
  host = data['host']
  hostrel = data['hostrel']
  count, html, summary = convert(html, host, hostrel)
  print(summary)
  return json.dumps({'count': count, 'html': html, 'summary': summary})

def add_hostname(url, host, hostrel):
  if url.startswith('//'):
    return 'http:' + url
  elif url.startswith('http'):
    return url
  elif url.startswith('/'):
    return host.rstrip('/') + url
  else:
    return host.rstrip('/') + hostrel.replace("[^/]*$", "/") + url

def capme(host, hostrel, x):
  a, b = analyze_image(add_hostname(x, host, hostrel))
  return b + " (" + ', '.join(a) + ")"

def convert(html, host, hostrel):
  if not host.startswith('http'):
    host = 'http://' + host
  soup = BeautifulSoup(html, 'html.parser')
  do_things_to_html(soup, word_color, lambda x: capme(host, hostrel, x))
  count = word_count(soup)
  summary = summarize(all_text(soup))
  return count,minify(soup.prettify()).encode('utf-8'), summary 

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
  """
  json_text = {'url': image_url}
  headers = {'Ocp-Apim-Subscription-Key': '12a4c0f569884fe5b4c528b51dc890b3'}
  res = requests.post('https://api.projectoxford.ai/vision/v1.0/describe',
                       headers=headers,
                       json=json_text)

  jres = json.loads(res.text)
  """
  jres = rapid.call('MicrosoftComputerVision', 'describeImage', {
    'image': image_url,
    'subscriptionKey': '12a4c0f569884fe5b4c528b51dc890b3',
    'maxCandidates': ''
  });

  return (
    jres[u'description'][u'tags'],
    jres[u'description'][u'captions'][0][u'text'] if len(jres[u'description'][u'captions']) else ''
  )
  
def analyze_image(image_url, tag_limit=10): 
  """
  Given an image_url and a tag_limit, make requests to both the Clarifai API
  and the Microsoft Congnitive Services API to return two things:

    (1) A list of tags, limited by tag_limit,
    (2) A description of the image
  """
  clarifai_tags = clarifai_analysis(image_url)
  ms_tags, ms_caption = oxford_project_analysis(image_url)

  clarifai_tags = map(lambda s: s.lower(), clarifai_tags)
  ms_tags = map(lambda s: s.lower(), ms_tags)

  # Get tags that occur in both
  merged_tags = []
  set(ms_tags)
  for tag in clarifai_tags:
    if tag in ms_tags:
      merged_tags.append(tag)
 
  merged_tags_set = set(merged_tags)
  merged_tags += [tag for tag in clarifai_tags if tag not in merged_tags]
  merged_tags += [tag for tag in ms_tags if tag not in merged_tags]

  # Limit the tags
  merged_tags = merged_tags[:tag_limit]

  return merged_tags, ms_caption

def pos_tagging(text):
  """
  Given some text as input, return the part of speech tagging as determined by
  the Microsoft Cognitive Services API.
  """
  #json_txt = {'language': 'en',
  #        'analyzerIds' : ["4fa79af1-f22c-408d-98bb-b7d7aeef7f04"],
  #        'text': text}
  #headers = {'Ocp-Apim-Subscription-Key': '6728888dd73c45ada252a5f46cb0ccba'}
  #res = requests.post('https://api.projectoxford.ai/linguistics/v1.0/analyze',
  #                     headers=headers,
  #                     json=json_txt)
  #
  #jres = json.loads(res.text)
  #if 'error' in jres:

  #return jres[0]['result'][0]
  return [tup[1] for tup in tagger.tag(nltk.word_tokenize(text))]

def word_color(text):
  """
  Given some text as input, run part of speech tagging and return a list in the
  form:

    [('The ', 'red'), ('cat ', 'blue') ... ]
  """
  words = nltk.word_tokenize(text)
  pos_tags = pos_tagging(text)

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

  word_tups[-1] = (
    word_tups[-1][0] + text[i:],
    word_tups[-1][1]
  )

  # Merge the tups if incorrectly split by tokenizer, give them a new 
  # pos tag: 'INV'
  merged_word_tups = []
  last_tup = (' ','')
  for tup in word_tups:
    if last_tup[0][-1].isalpha():
      last_tup = (
        last_tup[0] + tup[0],
        last_tup[1]
      )
    else:
      merged_word_tups.append(last_tup)
      last_tup = tup

  merged_word_tups.append(last_tup)
  merged_word_tups = merged_word_tups[1:]

  if 'interchange' in text and len(word_tups) != len(merged_word_tups):
    print(len(pos_tags))
    print(i)
    print(j)
    print(text)
    print(word_tups)
    print(merged_word_tups)

  return merged_word_tups

def summarize(text, target_sentences=3):
  """
  Given all the text in a page, determine a number of summarizing sentences.
  """

  def page_rank(G, s = .85, maxerr = .001):
    G = np.array(G)

    n = G.shape[0]

    # transform G into markov matrix M
    M = csc_matrix(G,dtype=np.float)
    rsums = np.array(M.sum(1))[:,0]
    ri, ci = M.nonzero()
    M.data /= rsums[ri]

    # bool array of sink states
    sink = rsums==0

    # Compute pagerank r until we converge
    ro, r = np.zeros(n), np.ones(n)
    while np.sum(np.abs(r-ro)) > maxerr:
      ro = r.copy()
      # calculate each pagerank at a time
      for i in xrange(0,n):
        # inlinks of state i
        Ii = np.array(M[:,i].todense())[:,0]
        # account for sink states
        Si = sink / float(n)
        # account for teleportation to state i
        Ti = np.ones(n) / float(n)

        r[i] = ro.dot( Ii*s + Si*s + Ti*(1-s) )

    # return normalized pagerank
    return r/sum(r)

  def vec_tfidf(sent):
    words = map(lambda s: s.lower(), nltk.word_tokenize(sent))
    counts = {}
    for w in words:
      if w not in counts:
        counts[w] = 0

      counts[w] += 1

    max_count = max(counts.values())

    tfidf = {}
    for word in counts.keys():
      tfidf[word] = (0.5 + 0.5*counts[word]/max_count) 
      tfidf[word] *= math.log(1 + brown_sent_count/total_word_counts.get(word,1))

    return tfidf

  def cos_similarity(vec1, vec2):
    num = 0
    denom = sum(vec1.values()) * sum(vec2.values())
    for e in vec1.keys():
      if e in vec2:
        num += vec1[e]*vec2[e]

    return 1.0 * num / denom

  tfidf = []
  sentences = tokenize.sent_tokenize(text)
  for sent in sentences:
    tfidf.append(vec_tfidf(sent))

  matrix = []
  for v1 in tfidf:
    row = []
    for v2 in tfidf:
      row.append(cos_similarity(v1, v2))
    matrix.append(row)

  scores = page_rank(matrix)

  return [sentences[i] for i in sorted(range(len(scores)), key=lambda x: -scores[x])][:target_sentences]

def main():
  print word_color("The cat in the hat likes funny memes -- I do too!")
  import pdb; pdb.set_trace()
  convert("""
<!DOCTYPE html>
<html>
<body>

<h1>My First Heading</h1>

<p>My first paragraph.</p>

</body>
</html>
  """, "localhost", "localhost")
  context = ('cert.pem', 'key.pem')
  app.run(debug=False, use_reloader=False, host='0.0.0.0', ssl_context=context)

if __name__ == '__main__':
  main()
