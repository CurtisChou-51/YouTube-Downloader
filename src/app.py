from flask import Flask, request, jsonify, send_from_directory, send_file, after_this_request
from pytubefix import YouTube
import os
from datetime import datetime
import certifi
import ssl
import urllib.request
import json
import re

context = ssl.create_default_context(cafile=certifi.where())
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
urllib.request.install_opener(opener)
mount_path = '/tmp/download'

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# this branch execute ffmpeg in the container
@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    try:
        yt = YouTube(data['url'])
        save_dir = create_save_dir()
        audio_error = save_audio(yt, save_dir)
        video_error = None if data['audioOnly'] else save_video(yt, save_dir)
        exec_ffmprg(save_dir, yt.title)

        dir_name = os.path.basename(save_dir)
        if audio_error or video_error:
            return jsonify({'message': audio_error or video_error, 'dir_name': dir_name})
        return jsonify({'message': 'success', 'dir_name': dir_name})
    except Exception as e:
        return jsonify({'message': str(e)}), 404

@app.route('/get_file', methods=['POST'])
def get_file():
    save_dir = os.path.join(mount_path, request.args.get('dir_name'))

    @after_this_request
    def delete_file(response):
        try:
            for file_name in os.listdir(save_dir):
                os.remove(os.path.join(save_dir, file_name))
        except Exception as ex:
            print(ex)
        return response

    if not os.path.exists(save_dir):
        return None

    for file_name in os.listdir(save_dir):
        if file_name.endswith('.mp4'):
            return send_file(os.path.join(save_dir, file_name), as_attachment=True)
    return None

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

def exec_ffmprg(save_dir, title):
    sanitized_title = re.sub(r'[\\/*?:"<>|]', "", title)

    video_filename = os.path.join(save_dir, 'video')
    audio_filename = os.path.join(save_dir, 'audio')
    output_filename = os.path.join(save_dir, f'{sanitized_title}.mp4')

    if os.path.exists(video_filename) and os.path.exists(audio_filename):
        os.system(f'ffmpeg -i {video_filename} -i {audio_filename} -c:v copy -c:a libmp3lame "{output_filename}"')
        os.remove(video_filename)
        os.remove(audio_filename)
    elif os.path.exists(audio_filename):
        os.system(f'ffmpeg -i {audio_filename} -c:a libmp3lame "{output_filename}"')
        os.remove(audio_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# You can change the resolution of the video stream by changing the resolution parameter in the video_stream variable.
# Note: If a video isn't available in the specified resolution, the downloaded video will be empty.