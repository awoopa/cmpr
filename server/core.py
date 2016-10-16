from bs4 import BeautifulSoup
from urllib import urlopen

known_tags = ['NN', 'VBZ', 'INV']

def visible(element):
  import re
  if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
    return False
  elif re.match('<!--.*-->', unicode(element)):
    return False
  elif unicode(element).strip() == '':
    return False
  return True

def retrieve_text(soup):
  texts = soup.find_all(string=True)
  return filter(visible, texts)

def retrieve_images(soup):
  return soup.find_all('img')

def word_count(soup):
  texts = soup.find_all(string=True)
  return sum(map(lambda s: len(s.split()), (filter(visible, texts))))

def all_text(soup):
  texts = soup.find_all(string=True)
  return " ".join(map(unicode, filter(visible, texts)))

def tokenize(text):
  from random import randint
  return [(i, 'NN' if randint(0, 1) == 0 else 'VBZ') for i in text.split()]

def do_things_to_html(soup, tokenizer, describer):
  style = soup.new_tag('style', type='text/css')
  style.append(
'''
.cNN,
.cNNP,
.cNNPS,
.cNNS,
.cPRP {
    color: #CC1E5C;
}
.cVB,
.cVBD,
.cVBG,
.cVBN,
.cVBP,
.cVBZ {
    color: #57B9CC;
}
.cRB,
.cRBR,
.cRBS,
.cJJ,
.cJJR,
.cJJS {
    color: #96CC2A;
}

.cINV {
    color: brown
}
.cFIG { display: inline-block; margin: 0 }
a {
    text-decoration: underline !important
}
''')
  if not soup.head:
    head = soup.new_tag('head')
    soup.html.append(head)

  soup.head.append(style)
  for node in retrieve_text(soup):
    text = unicode(node)
    tokens = tokenizer(text)

    cur_node = None
    for (text, code) in tokens:
      tag = soup.new_tag('span', **{'class': 'c' + code})
      tag.string = text
      if cur_node:
        cur_node.insert_after(tag)
        cur_node = tag
      else:
        node.replace_with(tag)
        cur_node = tag
  for node in retrieve_images(soup):
    src = node.attrs['src']
    fig = soup.new_tag('figure', **{'class': 'cFIG'})
    caption = soup.new_tag('figcaption')
    try:
      caption.string = describer(src)
    except:
      pass
    node.replace_with(fig)
    fig.append(node)
    node.insert_after(caption)

def test():
	from urllib import urlopen
	soup = BeautifulSoup(urlopen("http://en.wikipedia.org/wiki/Electron").read(), "html.parser")
	do_things_to_html(soup, tokenize, lambda x: x)
	with open('test.html', 'w') as f:
		f.write(soup.prettify().encode('utf-8'))

test()
