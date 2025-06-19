import os

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

# Cache the system prompt
cached_system_prompt = {
    "type": "text",
    "text": """
You're an expert in creating clean, visually engaging Manim animations to explain STEM concepts.
Follow these rules strictly:
    - The animation visually explains the concept clearly.
    - Output only Manim code, nothing else.
    - Use minimal text. Rely on visual explanation and dynamic animations instead.
    - Lay out all elements clearly — no overlaps or visual clutter. Use proper alignment and spacing.
    - Animate transitions and emphasize relationships (e.g. arrows, movement, highlights).
    - When writing text before rendering new text clear the existing text using the FadeOut function to avoid cluttering
    - Do not try to draw circuit diagrams   
    - Use modern Manim syntax.
Your goal is to make each animation look great and clearly explain the concept through motion.
""",
    "cache_control": {"type": "ephemeral"},
}


def create_video():
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        system=[cached_system_prompt],
        messages=[
            {
                "role": "user",
                "content": "Create an animation explaining the doppler effect",
            }
        ],
    )

    with open("video_file.py", "w") as f:
        text = message.content[0].text.replace("```python", "").replace("```", "")
        f.write(text)
    pass
