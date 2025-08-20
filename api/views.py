from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from dotenv import load_dotenv
import random
from django.views.decorators.http import require_GET
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
    return completion.choices[0].message.content

def extract_video_id(url):
    if "youtube.com/watch?v=" in url:
        url = url.split("v=")[1]
        if "&" in url:
            url = url.split("&")[0]
        return url

    elif "youtu.be/" in url:
        url = url.split(".be/")[1]
        if "?" in url:
            url = url.split("?")[0]
        return url

    return None

proxy_list = [
    "23.95.150.145:6114:xkruocsa:kjjvz8xrd626",
    "198.23.239.134:6540:xkruocsa:kjjvz8xrd626",
    "45.38.107.97:6014:xkruocsa:kjjvz8xrd626",
    "107.172.163.27:6543:xkruocsa:kjjvz8xrd626",
    "64.137.96.74:6641:xkruocsa:kjjvz8xrd626",
    "45.43.186.39:6257:xkruocsa:kjjvz8xrd626",
    "154.203.43.247:5536:xkruocsa:kjjvz8xrd626",
    "216.10.27.159:6837:xkruocsa:kjjvz8xrd626",
    "136.0.207.84:6661:xkruocsa:kjjvz8xrd626",
    "142.147.128.93:6593:xkruocsa:kjjvz8xrd626",
]


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

            # ✅ Proxy handling updated
            chosen_proxy = random.choice(proxy_list)
            ip, port, user, pwd = chosen_proxy.split(":")
            proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
            proxies = {"http": proxy_url, "https": proxy_url}

            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['en', 'en-GB'],
                proxies=proxies
            )

            transcript_text = "\n".join([entry['text'] for entry in transcript])

            if len(transcript_text) >= 20000:
                return JsonResponse(
                    {"success": False, "error": "We don't support videos of this length"},
                    status=400
                )

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

@require_GET
def isallwell(request):
    return JsonResponse({"status": "ok"})
