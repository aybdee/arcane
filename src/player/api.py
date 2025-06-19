import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from google import genai
from google.genai import types

from player.arcane_prompt import ARCANE_PROMPT

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

app = FastAPI(title="Video Generator", version="1.0.0")

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
    - Use modern Manim syntax.
Your goal is to make each animation look great and clearly explain the concept through engaging animations and visuals.
""",
    "cache_control": {"type": "ephemeral"},
}


def generate_manim_code(topic: str) -> str:
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            system=[cached_system_prompt],
            messages=[
                {
                    "role": "user",
                    "content": f"Create an animation explaining {topic}",
                }
            ],
        )

        # Clean the code response
        code = (
            message.content[0].text.replace("```python", "").replace("```", "").strip()
        )
        return code
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate code: {str(e)}"
        )


def create_and_render_video(code: str, output_dir: str) -> str:
    try:
        # Create the Python file
        python_file = os.path.join(output_dir, "animation.py")
        with open(python_file, "w") as f:
            f.write(code)

        cmd = [
            "manim",
            "animation.py",
            "mp4",
            "-o",
            "output.mp4",
        ]

        result = subprocess.run(
            cmd,
            cwd=output_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise print(f"Manim failed: {result.stderr}")

        # Find the generated video file
        media_dir = os.path.join(output_dir, "media", "videos", "animation", "480p15")
        video_file = os.path.join(media_dir, "output.mp4")

        if not os.path.exists(video_file):
            # Try alternative path structure
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        video_file = os.path.join(root, file)
                        break
                if video_file and os.path.exists(video_file):
                    break

        if not os.path.exists(video_file):
            raise Exception("Generated video file not found")

        return video_file

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Video generation timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render video: {str(e)}")


@app.get("/")
async def root():
    return {
        "message": "Manim Video Generator API",
        "endpoints": ["/generate-video/{topic}"],
    }


@app.get("/generate-video/{topic}")
async def generate_video(topic: str):

    # Create temporary directory for this request

    try:
        # Generate Manim code
        print(f"Generating code for prompt: {topic}....")
        code = generate_manim_code(topic)
        print(f"Generated code")

        # Create and render video

        print(f"Generating video...")
        video_path = create_and_render_video(code, "generated")
        print(f"Video generated at: {video_path}")

        # Copy video to a permanent location for serving
        output_filename = f"{topic.replace(' ', '_')}_animation.mp4"
        permanent_path = os.path.join("generated_videos", output_filename)

        # Ensure output directory exists
        os.makedirs("generated_videos", exist_ok=True)

        # Copy the video
        shutil.copy2(video_path, permanent_path)

        return FileResponse(
            path=permanent_path,
            media_type="video/mp4",
            filename=output_filename,
            headers={"Content-Disposition": f"attachment; filename={output_filename}"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary directory
        try:
            shutil.rmtree(temp_dir)
        except:
            pass  # Ignore cleanup errors


@app.get("/generate-arcane-code/{topic}")
async def generate_arcane_code(topic: str):
    """
    Generate Manim code for a given topic using Arcane.
    """
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=topic,
            config=types.GenerateContentConfig(system_instruction=ARCANE_PROMPT),
        )

        # Return the generated code
        return {"code": response.candidates[0].content.parts[0].text}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate code: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def custom_500_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "details": str(exc)},
    )
