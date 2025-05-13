from flask import Flask, render_template, request, jsonify
import pandas as pd
import os


app = Flask(__name__)

# โหลดข้อมูล
df = pd.read_csv('cleaned_songs.csv')

# โหลด feedback log
if os.path.exists('user_feedback_log.csv'):
    user_feedback_log = pd.read_csv('user_feedback_log.csv')
else:
    user_feedback_log = pd.DataFrame(columns=['mood', 'track_name', 'artist', 'rating', 'feedback'])

# filters สำหรับ mood
def recommend_playlist_for_mood(mood, shown_tracks=set(), playlist_size=5):
    filters = {
        'happy': df[df['valence'] > 0.7],
        'sad': df[df['valence'] < 0.3],
        'calm': df[df['energy'] < 0.4],
        'angry': df[(df['valence'] < 0.4) & (df['energy'] > 0.7)],
        'energetic': df[df['energy'] > 0.7],
        'romantic': df[(df['valence'] > 0.6) & (df['acousticness'] > 0.5)],
        'focus': df[(df['instrumentalness'] > 0.7) & (df['energy'] < 0.6)],
        'party': df[(df['danceability'] > 0.7) & (df['energy'] > 0.7)],
        'chill': df[(df['energy'] < 0.5) & (df['danceability'] > 0.5)],
        'dark': df[(df['valence'] < 0.3) & (df['acousticness'] < 0.3)],
        'dreamy': df[(df['acousticness'] > 0.6) & (df['valence'] > 0.4)],
        'motivated': df[(df['energy'] > 0.8) & (df['valence'] > 0.5)],
        'love': df[(df['valence'] > 0.6) & (df['acousticness'] > 0.4) & (df['energy'] < 0.6)],
        'rizz': df[(df['danceability'] > 0.75) & (df['valence'] > 0.5) & (df['energy'] > 0.6)],
        'hot': df[(df['danceability'] > 0.75) & (df['valence'] > 0.5) & (df['acousticness'] < 0.5) & (df['energy'] > 0.5)],
    }

    mood_df = filters.get(mood)
    if mood_df is None:
        return []
    

    mood_df = mood_df[~mood_df['track_name'].isin(shown_tracks)]
    return mood_df.sample(min(playlist_size, len(mood_df))).to_dict(orient='records')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_playlist', methods=['POST'])
def get_playlist():
    mood = request.form['mood']
    playlist = recommend_playlist_for_mood(mood)
    return jsonify(playlist)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    entry = pd.DataFrame([data])
    entry.to_csv('user_feedback_log.csv', mode='a', header=not os.path.exists('user_feedback_log.csv'), index=False)
    return jsonify({'status': 'success'})

print(df.columns)


if __name__ == '__main__':
    app.run(debug=True)

