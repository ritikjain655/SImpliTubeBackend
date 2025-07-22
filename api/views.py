from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_openai_client():
    apikey = os.getenv("OPEN_API_KEY")
    return OpenAI(api_key=apikey)

def summaryai(transcript_text):
    client = get_openai_client()
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[
            {"role": "system", "content": "You are a helpful assistant who provides summary of YouTube transcripts in 100-150 words"},
            {"role": "user", "content": transcript_text},
        ],
    )
    return completion.choices[0].message.content

def notesai(transcript_text):
    client = get_openai_client()
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[
            {"role": "system", "content": "You are a helpful assistant who makes notes from the YouTube transcript in 300 words"},
            {"role": "user", "content": transcript_text},
        ],
    )
    return completion.choices[0].message.content

def quizai(transcript_text):
    client = get_openai_client()
    completion = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=500,
        messages=[
            {"role": "system", "content": "You are a helpful assistant who creates 5 MCQ quiz questions from a YouTube transcript with answers after the 5th question"},
            {"role": "user", "content": transcript_text},
        ],
    )
    print(completion)
    return completion.choices[0].message.content
    
def extract_video_id(url):
    patterns = [
        "https://www.youtube.com/watch?v=",
        "http://www.youtube.com/watch?v=",
        "www.youtube.com/watch?v=",
        "youtube.com/watch?v=",
    ]
    for pattern in patterns:
        if url.startswith(pattern):
            return url.replace(pattern, "")
    return None

@csrf_exempt
def generate_content(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get("url")
            option = int(data.get("option"))

            video_id = extract_video_id(url)
            if not video_id:
                return JsonResponse({"error": "Invalid YouTube URL"}, status=400)

            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-GB'])
            transcript_text = "\n".join([entry['text'] for entry in transcript])

            if option == 1:
                result = summaryai(transcript_text)
            elif option == 2:
                result = notesai(transcript_text)
            elif option == 3:
                result = quizai(transcript_text)
            else:
                return JsonResponse({"success": False, "error": "Invalid option"}, status=400)

            return JsonResponse({"success": True, "data": result})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"message": "Only POST method allowed"}, status=405)
