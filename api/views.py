from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import os
from dotenv import load_dotenv
import random

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
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10000",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10006",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10010",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10013",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10019",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10021",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10025",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10034",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10038",
    "hxLHJB4jTe2DAto:Ycs4J5SAPSBx1L9@146.70.146.102:10039",
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

            chosen_proxy = random.choice(proxy_list)
            proxy_url = f"http://{chosen_proxy}"
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id,
                languages=['en', 'en-GB'],
                proxies={'https': proxy_url}
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


def isallwell(request):
    return JsonResponse({"status": "ok"})