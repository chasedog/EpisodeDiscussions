from flask import Flask, jsonify, render_template
import test, stats, os
app = Flask(__name__)

cache = {}

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/r/<string:subreddit>')
def episodes(subreddit):
    seasonsAndEpisodes = _getEpisodesBySeason(subreddit)
    return render_template('index.html', result=seasonsAndEpisodes, subreddit=subreddit)

@app.route('/api/r/<string:subreddit>', methods=['GET'])
def get_episodes(subreddit):
    """
    Endpoint for the GET REST API call.
    Retrieves episodes by season from the specified subreddit and serializes them into JSON.
    """

    episodesBySeason = _getEpisodesBySeason(subreddit)
    seasons = [season.serialize() for season in episodesBySeason]
    result = {"seasons": seasons, "subreddit": subreddit}
    return jsonify(result)

def _getEpisodesBySeason(subreddit):
    """
    Private method.
    Retrieves episodes by season from the specified subreddit.
    """

    # Cache only works locally
    if subreddit in cache:
        return cache[subreddit]

    episodes = test.getValidData(subreddit)
    seasonsAndEpisodes = stats.extractSeasonsAndEpisodes(episodes)
    cache[subreddit] = seasonsAndEpisodes
    return seasonsAndEpisodes

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))
    app.run(debug=True, host='0.0.0.0', port=port)