from dotenv import load_dotenv
from flask import Blueprint, jsonify, request as req, Response
from openai import OpenAI
import os
import requests
from tasks.calls import transcribe_call, get_suggestions

bp = Blueprint('calls_routes', __name__)

load_dotenv()
auth_token = os.getenv('auth_token')
ghl_url = os.getenv('ghl_v2_api')
gpt = os.getenv('gpt_token')
org = os.getenv('gpt_org')
client = OpenAI(api_key=gpt, organization=org)


# Store suggestions into Client Harbor
@bp.route('/post_call_suggestions', methods=['POST'])
def call_suggestions():
    data = req.get_json()
    client_id = data.get('client_id')
    field_id = data.get('field_id')

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
        'Version': '2021-07-28'
    }

    response = requests.get(f'{ghl_url}contacts/{client_id}', headers=headers)
    if response.status_code == 200:
        user = response.json()["contact"]
        transcript = None
        
        for field in user["customFields"]:
            if field["id"] == field_id:
                print(field["value"])
                transcript = transcribe_call(field["value"])
                print(transcript)
        
        analysis = get_suggestions(transcript)
        resp = Response(
            response=analysis,
            status=200
        )
        return resp
                
    elif response.status_code == 400:
        return Response(status=400)

    return Response(status=500)

