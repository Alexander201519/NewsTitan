from flask import Flask, render_template, jsonify, request
import requests
import random
import urllib.parse

app = Flask(__name__)

# ALL CATEGORIES RESTORED + POLITICS ADDED
SOURCES = {
    "General": ["worldnews", "news", "internationalnews"],
    "Politics": ["politics", "ukpolitics", "worldpolitics"], 
    "Tech": ["technology", "tech", "gadgets"],
    "Weird": ["nottheonion", "offbeat", "weirdnews"],
    "Gaming": ["gaming", "games", "pcgaming"],
    "Entertainment": ["entertainment", "movies", "television"],
    "LongReads": ["longreads", "InDepthStories", "TrueReddit"],
    "Sports": ["sports", "nba", "soccer"]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_news')
def get_news():
    category = request.args.get('category', 'General')
    search = request.args.get('search', '').strip()
    source_domain = request.args.get('source', '')
    
    headers = {'User-agent': f'NewsHubOmni_v19_{random.randint(1,999)}'}
    
    # LOGIC: If user searches or picks a specific source (BBC, etc)
    if search or source_domain:
        query = f"{search} site:{source_domain}" if source_domain else search
        safe_q = urllib.parse.quote(query)
        url = f"https://www.reddit.com/search.json?q={safe_q}&sort=new&limit=25"
    else:
        # LOGIC: Standard Category Browsing
        sub_list = SOURCES.get(category, ["news"])
        sub = random.choice(sub_list)
        url = f"https://www.reddit.com/r/{sub}/hot.json?limit=40"

    try:
        res = requests.get(url, headers=headers, timeout=5).json()
        posts = [p['data'] for p in res['data']['children'] if not p['data'].get('stickied')]
        if not posts: return jsonify({"error": "No results found."})
        
        story = random.choice(posts)
        img = ""
        try:
            img = story['preview']['images'][0]['source']['url'].replace("&amp;", "&")
        except:
            if story.get('thumbnail', '').startswith('http'): img = story['thumbnail']

        return jsonify({
            "title": story['title'],
            "url": story['url'],
            "image": img,
            "source": f"r/{story['subreddit']}",
            "author": story['author']
        })
    except:
        return jsonify({"error": "Connection failed"})

if __name__ == '__main__':
    app.run(debug=True)