from flask import Flask, request, jsonify, send_from_directory, send_file
from pytubefix import YouTube
import os
from datetime import datetime
import certifi
import ssl
import urllib.request

context = ssl.create_default_context(cafile=certifi.where())
opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
urllib.request.install_opener(opener)

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/mp3')
def mp3():
    return send_from_directory('.', 'mp3.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data['url']
    audio_only = data['audioOnly'].strip().lower() == 'yes'

    video = YouTube(url)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if audio_only:
        audio_stream = video.streams.filter(only_audio=True).order_by('abr').desc().first()
        audio_filename = f'audio_{timestamp}.m4a'
        output_filename = f'audio_{timestamp}.mp3'
        audio_stream.download(filename=audio_filename)
        os.system(f'ffmpeg -i {audio_filename} -q:a 0 -map a {output_filename}')
        os.remove(audio_filename)
        return send_file(output_filename, as_attachment=True)
    else:
        video_stream = video.streams.filter(progressive=False, file_extension='mp4', resolution='1080p').order_by('resolution').desc().first()
        if not video_stream:
            return jsonify({'message': 'No suitable video stream found'}), 404
        video_filename = f'video_{timestamp}.mp4'
        audio_filename = f'audio_{timestamp}.m4a'
        output_filename = f'output_{timestamp}.mp4'
        video_stream.download(filename=video_filename)
        audio_stream = video.streams.filter(only_audio=True).order_by('abr').desc().first()
        audio_stream.download(filename=audio_filename)
        os.system(f'ffmpeg -i {video_filename} -i {audio_filename} -c:v libx264 -c:a aac -y {output_filename}')
        os.remove(video_filename)
        os.remove(audio_filename)
        return send_file(output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

# You can change the resolution of the video stream by changing the resolution parameter in the video_stream variable.
# Note: If a video isn't available in the specified resolution, the downloaded video will be empty.