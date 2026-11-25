import asyncio
import os
import subprocess
import urllib.parse
import requests
import edge_tts

os.makedirs("demo_out", exist_ok=True)

# 1. Mini Storyboard (3 shots x 5 seconds = 15 seconds)
SHOTS = [
    {
        "id": "shot_1",
        "duration": 5,
        "prompt": "Warm sunrise over misty green hills in Ethiopia, cinematic film grain, 1970s vintage photo style",
        "text": "Every family carries a story that begins before we are born."
    },
    {
        "id": "shot_2",
        "duration": 5,
        "prompt": "Close up of traditional clay coffee pot jebena steaming on a wooden table, warm morning light, cinematic",
        "text": "Over morning coffee, my grandmother finally told me hers."
    },
    {
        "id": "shot_3",
        "duration": 5,
        "prompt": "An old handwritten letter and vintage brass key resting beside a window, soft golden hour light",
        "text": "It started with a single letter that changed everything."
    }
]

VOICE = "en-US-AndrewNeural"  # Change to "am-ET-AmehaNeural" for Amharic!


async def generate_narration():
    full_text = " ".join(s["text"] for s in SHOTS)
    communicate = edge_tts.Communicate(full_text, VOICE)
    submaker = edge_tts.SubMaker()
    with open("demo_out/voice.mp3", "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    with open("demo_out/subs.srt", "w", encoding="utf-8") as sub_file:
        sub_file.write(submaker.get_srt())
    print("1. Narration and subtitles created.")


# POLLINATIONS_KEY = "sk_QYIY5K4PdvvfxEAPzrVYvfZn0miED5YJ"


# def generate_images():
#     for shot in SHOTS:
#         encoded = urllib.parse.quote(shot["prompt"])
#         url = f"https://gen.pollinations.ai/image/{encoded}?model=flux&width=1280&height=720&key={POLLINATIONS_KEY}"
#         response = requests.get(url, timeout=60)
#         response.raise_for_status()
#         with open(f"demo_out/{shot['id']}.jpg", "wb") as f:
#             f.write(response.content)
#         print(f"2. Image generated: {shot['id']}.jpg")


def animate_shots():
    for shot in SHOTS:
        frames = shot["duration"] * 30
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", f"demo_out/{shot['id']}.jpg",
            "-vf", f"scale=1920:1080,zoompan=z='min(zoom+0.001,1.15)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720",
            "-c:v", "libx264", "-t", str(shot["duration"]
                                         ), "-pix_fmt", "yuv420p",
            f"demo_out/{shot['id']}.mp4"
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, check=True)
        print(f"3. Animated clip: {shot['id']}.mp4")


def assemble_video():
    with open("demo_out/list.txt", "w", encoding="utf-8") as f:
        for shot in SHOTS:
            f.write(f"file '{shot['id']}.mp4'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "demo_out/list.txt",
        "-i", "demo_out/voice.mp3",
        "-vf", "subtitles=demo_out/subs.srt:force_style=FontSize=22\\,PrimaryColour=&H00FFFFFF\\,OutlineColour=&H00000000\\,BorderStyle=3",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
        "demo_out/final_test.mp4"
    ]
    subprocess.run(cmd, check=True)
    print("4. Done! Watch demo_out/final_test.mp4")


if __name__ == "__main__":
    asyncio.run(generate_narration())
    # generate_images()
    animate_shots()
    assemble_video()
