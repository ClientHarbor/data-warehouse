from dotenv import load_dotenv
from openai import OpenAI
import os
import requests

load_dotenv()
gpt = os.getenv('gpt_token')
org = os.getenv('gpt_org')
client = OpenAI(api_key=gpt, organization=org)

'''
transcribe_call
Purpose: Takes in a wav file from url that is provided and then returns a raw transcription, without any timestamps.
Args: call - wav file url
Returns: A string of the transcription captured

'''
def transcribe_call(call):
    transcript = None

    response = requests.get(call, stream=True)
    if response.status_code != 200:
        raise ValueError("Failed to download audio file. Check the link.")

    temp_file_path = "temp_audio_file.wav"
    with open(temp_file_path, "wb") as temp_file:
        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)
    
    with open(temp_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            temperature=0.8
        )

    os.remove(temp_file_path)
    return transcript.text


'''
get_suggestions
Purpose: reads a transcription and provides an analysis on the content and also suggestions
         follow ups and future calls.
Args: transcript - str
Returns: object - provides object with details on key points, mood of conversation, and mistakes
                  suggestions.
'''
def get_suggestions(transcript):
    system_prompt = """
    You are a Senior Behavioral Analyst with a focus on conversation. You 
    focus on high-level patterns in human behavior and communication, often integrating psychological 
    or social research into actionable strategies. You develop and optimize strategies for how organizations 
    interact with clients or stakeholders based on detailed conversation analytics. When given a transcript or
    a text convseration, you will analyze it, determine the flow, and then offer suggestions in making the next 
    conversation with the client better.
    """

    user_prompt = f"""
    Hello, I need help analyzing the next steps for my conversation. 
    I'm not great at reading emotions, so I struggle to understand what happened. 

    Here is the transcript of my conversation: 
    {transcript}

    Can you please:
    1. Summarize the key points of the conversation.
    2. Analyze the mood of the conversation.
    3. Indicate if any deals were made or if I need to follow up with another call or text.
    4. Highlight any mistakes I made during the conversation and suggest how I can improve in the future.
    5. If there were severe mistakes, let me know if I need to apologize in the next call or text (assuming I haven't already).

    Thank you for your assistance!
    """

    format = {
        "type" : "json_schema",
        "json_schema" : {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "key_points": {
                        "description": "provide a list of the key points of the conversation",
                        "type": "string",
                    },
                    "mood": {
                        "description": "provide the mood of the conversation and notice and switch between moods",
                        "type": "string"
                    },
                    "deals": {
                        "description": "was an offer made in the conversation",
                        "type": "boolean"
                    },
                    "suggestions": {
                        "description": "provide the mistakes and follow up with the suggestions necessary for a better next call",
                        "type": "string",
                    },
                    "additionalProperties": False
                }
            }
        }
    }

    json_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        response_format=format
    )

    return json_completion.choices[0].message.content