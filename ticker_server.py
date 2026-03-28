from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import threading
import urllib.parse
import os

APP_PORT = int(os.environ.get('PORT', 5000))
CACHE_TTL = 15  # seconds

app = Flask(__name__, static_url_path='/static', static_folder='static')
CORS(app)

# simple in-memory cache: url -> {'updated_at': ts, 'data': {...}}
cache = {}
cache_lock = threading.Lock()


def mock_data():
    now = datetime.utcnow().isoformat() + 'Z'
    return {
        'name': 'Sample Challonge Tournament',
        'current_matches': [
            {'player1': 'Vudujin', 'player2': 'Harry',
                'score1': 2, 'score2': 0, 'state': 'complete'}
        ],
        'upcoming_matches': [
            {'player1': 'PumpkinButter', 'player2': 'Thrik'},
            {'player1': 'Phreeze', 'player2': 'Kao'}
        ],
        'updated_at': now
    }


def fetch_tournament_from_html(url):
    # Try to fetch and parse a Challonge public tournament page.
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, 'html.parser')

    # Attempt to extract tournament name
    title = None
    h1 = soup.find('h1')
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    if not title:
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title.get('content')

    # Basic heuristic for matches: search for elements that look like match rows
    current = []
    upcoming = []

    # look for elements with class including 'match' or 'bracket' or 'game'
    match_nodes = soup.find_all(class_=lambda c: c and (
        'match' in c or 'bracket' in c or 'game' in c))
    for node in match_nodes:
        texts = [t.get_text(strip=True) for t in node.find_all(
            ['div', 'span', 'p', 'td']) if t.get_text(strip=True)]
        if len(texts) >= 2:
            # heuristic: last items might be scores
            p1 = texts[0]
            p2 = texts[1]
            score1 = None
            score2 = None
            # try to find numeric tokens
            nums = [t for t in texts if t.isdigit()]
            if len(nums) >= 2:
                score1 = int(nums[0])
                score2 = int(nums[1])
            item = {'player1': p1, 'player2': p2}
            if score1 is not None:
                item.update(
                    {'score1': score1, 'score2': score2, 'state': 'unknown'})
                current.append(item)
            else:
                upcoming.append(item)

    # fallback: if no parsed matches, return None to indicate failure
    if not title and not current and not upcoming:
        return None

    return {
        'name': title or 'Challonge Tournament',
        'current_matches': current,
        'upcoming_matches': upcoming,
        'updated_at': datetime.utcnow().isoformat() + 'Z'
    }


def get_cached(url):
    now = time.time()
    with cache_lock:
        entry = cache.get(url)
        if entry and now - entry['ts'] < CACHE_TTL:
            return entry['data']
    return None


def set_cache(url, data):
    with cache_lock:
        cache[url] = {'ts': time.time(), 'data': data}


@app.route('/api/mock')
def api_mock():
    return jsonify(mock_data())


@app.route('/api/tournament')
def api_tournament():
    url = request.args.get('url')
    use_mock = request.args.get(
        'mock', 'false').lower() in ('1', 'true', 'yes')
    force = request.args.get('force', 'false').lower() in ('1', 'true', 'yes')

    if use_mock or not url:
        return jsonify(mock_data())

    url = urllib.parse.unquote_plus(url)

    if not force:
        cached = get_cached(url)
        if cached:
            return jsonify(cached)

    data = fetch_tournament_from_html(url)
    if data is None:
        # parsing failed, fall back to mock
        data = mock_data()

    set_cache(url, data)
    return jsonify(data)


@app.route('/')
def root():
    return app.send_static_file('dashboard.html')


if __name__ == '__main__':
    print('Starting ticker_server on port', APP_PORT)
    app.run(host='0.0.0.0', port=APP_PORT, debug=True)
