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
  print(soup)
  texts = soup.find_all(string=True)
  print(texts)
  return filter(visible, texts)

def tokenize(text):
  from random import randint
  return [(i, 'NN' if randint(0, 1) == 0 else 'VBZ') for i in text.split()]

def do_things_to_html(soup, tokenizer):
  style = soup.new_tag('style', type='text/css')
  style.append(
      '''.cNN {
      color: red
  }
  .cVBZ {
      color: blue
  }
  .cINV {
      color: brown
  }
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

def test():
	soup = BeautifulSoup("""
<!DOCTYPE html>
<html>
<body>

<h1>My First Heading</h1>

<p>My first paragraph.</p>

</body>
</html>
""", "html.parser")
	do_things_to_html(soup, tokenize)
	print(soup)

test()
