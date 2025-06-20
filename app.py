from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

@app.route('/')
def home():
    return "✅ Wikipedia Quantum API is running! Use /search?query=your_term"

@app.route('/search', methods=['GET'])
def search_wikipedia():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400

    # Fetch search results from Wikipedia
    search_response = requests.get(WIKIPEDIA_API_URL, params={
        'action': 'query',
        'format': 'json',
        'list': 'search',
        'srsearch': query
    })

    search_data = search_response.json()

    if not search_data.get('query') or not search_data['query'].get('search'):
        return jsonify({'error': 'No results found'}), 404

    page_id = search_data['query']['search'][0]['pageid']

    # Fetch detailed info
    page_response = requests.get(WIKIPEDIA_API_URL, params={
        'action': 'query',
        'format': 'json',
        'prop': 'extracts|pageimages',
        'exintro': True,
        'explaintext': True,
        'pageids': page_id,
        'pithumbsize': 500
    })

    page_data = page_response.json()
    page = page_data['query']['pages'][str(page_id)]

    return jsonify({
        'title': page.get('title', 'Unknown Title'),
        'extract': page.get('extract', 'No description available.'),
        'image': page.get('thumbnail', {}).get('source', None),
        'page_url': f"https://en.wikipedia.org/?curid={page_id}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)