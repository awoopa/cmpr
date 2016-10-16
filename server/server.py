from clarifai.rest import ClarifaiApp

from flask import Flask, request, jsonify
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/convert_html', methods=['POST'])
def convert_html():
  """
  Given an HTML page as a string, apply all of our comprehension-improving
  transformations, and return the new HTML.
  """
  data = request.form
  html = data['page']
  return convert(html)

#import pdb; pdb.set_trace()
#app = ClarifaiApp(app_id='VWLdaFkl56G5o81k54s-ZI6se11adzKSFnVQ_Ggg', 
#                  app_secret='QnVFC6wRIWDplb3SZBVX5iMLje_tA9oWtyj8WpcH')
#
#model = app.models.get('general-v1.3')
#
#print model.predict_by_url('https://samples.clarifai.com/metro-north.jpg')

def main():
  app.run(debug=False, use_reloader=False)

if __name__ == '__main__':
  main()
