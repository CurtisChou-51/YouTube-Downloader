from flask import Flask, request, jsonify, send_from_directory, send_file
from pytubefix import YouTube
import os
from datetime import datetime
import certifi
import ssl
import urllib.request
import json

context = ssl.create_default_context(cafile=certifi.where())
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
urllib.request.install_opener(opener)
mount_path = '/tmp/download'

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Just save files to the mounted volume location
# ffmpeg conversion is executed outside of the Docker container on the host machine
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    try:
        yt = YouTube(data['url'])
        save_dir = create_save_dir()
        audio_error = save_audio(yt, save_dir)
        video_error = None if data['audioOnly'] else save_video(yt, save_dir)
        save_json(yt, save_dir)
        if audio_error or video_error:
            return jsonify({'message': audio_error or video_error}), 404
        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'message': str(e)}), 404

def create_save_dir():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    save_dir = os.path.join(mount_path, timestamp)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

def save_audio(yt, save_dir):
    audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    if not audio_stream:
        return 'No audio stream found'
    audio_stream.download(output_path=save_dir, filename='audio')
    return None

def save_video(yt, save_dir):
    video_stream = yt.streams.filter(progressive=False).order_by('resolution').desc().first()
    if not video_stream:
        return 'No suitable video stream found'
    video_stream.download(output_path=save_dir, filename='video')
    return None

def save_json(yt, save_dir):
    yt_info = {
        'title': yt.title,
        'length': yt.length,
        'views': yt.views,
        'author': yt.author,
        'publish_date': yt.publish_date.strftime('%Y-%m-%d')
    }
    with open(os.path.join(save_dir, 'ok.json'), 'w') as f:
        json.dump(yt_info, f)
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# You can change the resolution of the video stream by changing the resolution parameter in the video_stream variable.
# Note: If a video isn't available in the specified resolution, the downloaded video will be empty.