from flask import Flask, render_template, request, jsonify, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_formats')
def get_formats():
    video_url = request.args.get('url')
    if not video_url:
        return jsonify({"success": False, "message": "No URL provided."})

    ydl_opts = {
        'quiet': True,
        'extract_audio': False,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            formats = info.get('formats', [])

            download_options = []
            for f in formats:
                if f.get('height'):
                    option = {
                        'quality': f'{f["height"]}p',
                        'format_id': f['format_id'],
                        'ext': f['ext']
                    }
                    download_options.append(option)

            return jsonify({
                "success": True,
                "title": info['title'],
                "options": download_options
            })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/download')
def download():
    video_url = request.args.get('url')
    format_id = request.args.get('format_id')
    title = request.args.get('title')

    ydl_opts = {
        'format': format_id,
        'quiet': True,
        'outtmpl': f'downloads/{title}.%(ext)s',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            return send_from_directory('downloads', os.path.basename(filename), as_attachment=True)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    # Configure HTTPS
    app.run(debug=True, host='127.0.0.1', port=5000, ssl_context=('certs/cert.pem', 'certs/key.pem'))
