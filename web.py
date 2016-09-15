from flask import Flask, jsonify, render_template
import test, stats, os
app = Flask(__name__)

cache = {}

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/r/<string:subreddit>')
def episodes(subreddit):
    seasonsAndEpisodes = _getEpisodes(subreddit)
    return render_template('index.html', result=seasonsAndEpisodes, subreddit=subreddit)

@app.route('/api/r/<string:subreddit>', methods=['GET'])
def get_episodes(subreddit):
    seasonsAndEpisodes = _getEpisodes(subreddit)
    return jsonify([season.serialize() for season in seasonsAndEpisodes])

def _getEpisodes(subreddit):
    if subreddit in cache:
        return cache[subreddit]
    episodes = test.getData(subreddit)
    seasonsAndEpisodes = stats.extractSeasonsAndEpisodes(episodes)
    cache[subreddit] = seasonsAndEpisodes
    return seasonsAndEpisodes

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(debug=True, host='0.0.0.0', port=port)