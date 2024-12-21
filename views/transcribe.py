from dotenv import load_dotenv
from flask import Blueprint, jsonify, request as req, Response
import json
import os
import requests
from tasks.transcribe import *

bp = Blueprint('transcribe_routes', __name__)


@bp.route('/youtube_transcript', methods=['POST'])
def transcribe_video():
    data = req.get_json()
    youtube_link = data.get('link')

    video_id = extract_video_id(youtube_link)
    transcript = transcribe(video_id)
    

    response = {
        "transcription": transcript
    }

    return Response(
        response=json.dumps(response),
        status=200,
        mimetype='application/json'
    )

# @bp.route('youtube_list_transcript', methods=['POST'])
# def transcribe_list_video():
#     data = req.get_json()
#     youtube_link = data.get('playlist_link')
    
