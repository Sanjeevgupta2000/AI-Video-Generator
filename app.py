import os
import uuid
import math
import numpy as np
import gradio as gr
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy.editor import ImageSequenceClip, AudioClip
from huggingface_hub import InferenceClient, get_token

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

HF_TOKEN = os.getenv("HF_TOKEN") or get_token()
IMAGE_MODEL = os.getenv("IMAGE_MODEL", "black-forest-labs/FLUX.1-schnell")
client = InferenceClient(token=HF_TOKEN)

CSS = """
body {
    background: #06111f !important;
}
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}
#hero {
    padding: 34px;
    border-radius: 22px;
    margin-bottom: 18px;
    color: white;
    background:
        linear-gradient(120deg, rgba(2,6,23,.92), rgba(15,23,42,.68)),
        url("https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=80&w=1600&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    box-shadow: 0 25px 80px rgba(0,0,0,.35);
}
#hero h1 {
    color: white;
    font-size: 56px;
    line-height: 1;
    margin: 0 0 10px;
}
#hero p {
    color: #dbeafe;
    font-size: 16px;
    max-width: 760px;
}
.block, .form, .tabitem {
    border-radius: 16px !important;
}
button.primary {
    background: linear-gradient(135deg, #14b8a6, #2563eb) !important;
    color: white !important;
}
footer {
    display: none !important;
}
"""

SCREEN_RECORDER = """
<iframe
  style="width:100%;height:560px;border:0;border-radius:18px;background:#020617;"
  allow="display-capture; microphone; camera"
  sandbox="allow-scripts allow-downloads allow-same-origin"
  srcdoc='
<!doctype html>
<html>
<head>
<style>
body {
  margin:0;
  font-family: Arial, sans-serif;
  background: radial-gradient(circle at top right, rgba(20,184,166,.28), transparent 30%),
              linear-gradient(135deg,#020617,#0f172a);
  color:white;
}
.wrap { padding:26px; }
h2 { font-size:32px; margin:0 0 8px; }
p { color:#cbd5e1; }
button, a {
  border:0;
  border-radius:12px;
  padding:13px 18px;
  color:white;
  font-weight:800;
  cursor:pointer;
  text-decoration:none;
  margin-right:10px;
}
#start { background:linear-gradient(135deg,#14b8a6,#0f766e); }
#stop { background:linear-gradient(135deg,#ef4444,#991b1b); }
#download { background:linear-gradient(135deg,#2563eb,#1e40af); display:none; }
video {
  width:100%;
  max-height:360px;
  background:#000;
  border-radius:14px;
  margin-top:16px;
}
#status { margin-top:14px; color:#a7f3d0; font-weight:800; }
</style>
</head>
<body>
<div class="wrap">
  <h2>Screen Recording Studio</h2>
  <p>Click start, choose your screen/window/tab, then stop and download the recording.</p>
  <button id="start">Start Screen Recording</button>
  <button id="stop" disabled>Stop Recording</button>
  <a id="download" download="screen-recording.webm">Download Recording</a>
  <div id="status">Ready to record.</div>
  <video id="preview" controls muted playsinline></video>
</div>

<script>
let recorder;
let chunks = [];
let stream;

const start = document.getElementById("start");
const stop = document.getElementById("stop");
const download = document.getElementById("download");
const preview = document.getElementById("preview");
const status = document.getElementById("status");

start.onclick = async () => {
  try {
    chunks = [];
    download.style.display = "none";

    stream = await navigator.mediaDevices.getDisplayMedia({
      video: true,
      audio: true
    });

    preview.srcObject = stream;
    await preview.play();

    recorder = new MediaRecorder(stream);

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(chunks, { type: "video/webm" });
      const url = URL.createObjectURL(blob);

      preview.srcObject = null;
      preview.src = url;
      preview.muted = false;

      download.href = url;
      download.style.display = "inline-block";

      status.innerText = "Recording stopped. Download is ready.";

      stream.getTracks().forEach(track => track.stop());
    };

    recorder.start();
    start.disabled = true;
    stop.disabled = false;
    status.innerText = "Recording screen now...";
  } catch (err) {
    status.innerText = "Screen recording failed: " + err.message;
  }
};

stop.onclick = () => {
  if (recorder && recorder.state !== "inactive") {
    recorder.stop();
  }
  start.disabled = false;
  stop.disabled = true;
};
</script>
</body>
</html>
'>
</iframe>
"""


def output_path(suffix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    return os.path.join(OUTPUT_DIR, f"{uuid.uuid4()}{suffix}")


def generate_image(prompt):
    if not prompt or not prompt.strip():
        raise gr.Error("Please enter a prompt.")

    try:
        image = client.text_to_image(prompt.strip(), model=IMAGE_MODEL)
    except Exception as exc:
        raise gr.Error(f"Image generation failed. Check Hugging Face login/token. Error: {exc}") from exc

    path = output_path("_image.png")
    image.save(path)
    return path, path, "Image generated successfully."


def build_prompt(subject, style):
    subject = subject or "a luxury product"
    prompt = (
        f"{subject}, {style}, cinematic lighting, professional commercial style, "
        "sharp details, realistic, clean background, premium composition, 4K"
    )
    caption = f"{subject.title()} looks unreal"
    return prompt, caption


def load_font(size, bold=False):
    names = ["arialbd.ttf", "arial.ttf"] if bold else ["arial.ttf", "arialbd.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()


def fit_cover(image, size, scale=1.0):
    target_w, target_h = size
    image = image.convert("RGB")
    src_w, src_h = image.size

    ratio = max(target_w / src_w, target_h / src_h) * scale
    new_w = int(src_w * ratio)
    new_h = int(src_h * ratio)

    image = image.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2

    return image.crop((left, top, left + target_w, top + target_h))


def wrap_text(draw, text, font, max_width):
    words = (text or "").split()
    lines = []
    current = ""

    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_frame(image, caption, subtitle, brand, progress, size, grade):
    frame = fit_cover(image, size, scale=1.0 + 0.08 * progress)

    if grade == "Vibrant":
        frame = ImageEnhance.Color(frame).enhance(1.25)
        frame = ImageEnhance.Contrast(frame).enhance(1.1)
    elif grade == "Cinematic":
        frame = ImageEnhance.Contrast(frame).enhance(1.15)
    elif grade == "Moody":
        frame = ImageEnhance.Brightness(frame).enhance(0.9)
        frame = ImageEnhance.Contrast(frame).enhance(1.2)

    frame = frame.convert("RGBA")
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    w, h = size
    title_font = load_font(max(34, w // 18), bold=True)
    sub_font = load_font(max(22, w // 32), bold=False)
    brand_font = load_font(max(18, w // 44), bold=True)

    margin = int(w * 0.06)
    card_h = int(h * 0.20)
    card_y = h - card_h - margin

    draw.rounded_rectangle(
        (margin, card_y, w - margin, card_y + card_h),
        radius=24,
        fill=(0, 0, 0, 165),
    )

    draw.rectangle(
        (margin, card_y, margin + int((w - margin * 2) * progress), card_y + 6),
        fill=(20, 184, 166, 255),
    )

    if brand:
        draw.rounded_rectangle(
            (margin, margin, margin + 260, margin + 52),
            radius=26,
            fill=(255, 255, 255, 225),
        )
        draw.text((margin + 20, margin + 14), brand.upper()[:22], fill=(15, 23, 42), font=brand_font)

    y = card_y + 34
    for line in wrap_text(draw, caption, title_font, w - margin * 4)[:2]:
        draw.text((margin + 34, y), line, fill="white", font=title_font)
        y += int(title_font.size * 1.15)

    if subtitle:
        y += 8
        for line in wrap_text(draw, subtitle, sub_font, w - margin * 4)[:2]:
            draw.text((margin + 34, y), line, fill=(226, 232, 240), font=sub_font)
            y += int(sub_font.size * 1.15)

    return Image.alpha_composite(frame, overlay).convert("RGB")


def make_audio(duration, music):
    if music == "None":
        return None

    freq = {
        "Chill": 196,
        "Cinematic": 130,
        "Upbeat": 246,
    }.get(music, 196)

    def audio_func(t):
        fade_in = np.minimum(1, t / 0.4)
        fade_out = np.minimum(1, (duration - t) / 0.6)
        env = np.maximum(0, np.minimum(fade_in, fade_out))
        return env * (
            0.05 * np.sin(2 * np.pi * freq * t)
            + 0.025 * np.sin(2 * np.pi * freq * 1.5 * t)
        )

    return AudioClip(audio_func, duration=duration, fps=44100)


def image_to_video(image_path, caption, subtitle, brand, aspect, duration, fps, grade, music):
    if image_path is None:
        raise gr.Error("Please upload or generate an image first.")

    size = (720, 1280) if aspect == "9:16 Short" else (1280, 720)
    duration = float(duration)
    fps = int(fps)
    total_frames = max(1, int(duration * fps))

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as exc:
        raise gr.Error(f"Could not open image: {exc}") from exc

    frames = []
    for i in range(total_frames):
        progress = i / max(1, total_frames - 1)
        frame = draw_frame(image, caption or "", subtitle or "", brand or "", progress, size, grade)
        frames.append(np.array(frame))

    out_path = output_path("_video.mp4")
    clip = ImageSequenceClip(frames, fps=fps)

    audio = make_audio(duration, music)
    if audio is not None:
        clip = clip.set_audio(audio)

    try:
        clip.write_videofile(
            out_path,
            fps=fps,
            codec="libx264",
            audio_codec="aac" if audio is not None else None,
            verbose=False,
            logger=None,
        )
    except Exception as exc:
        raise gr.Error(f"Video export failed: {exc}") from exc
    finally:
        clip.close()
        if audio is not None:
            audio.close()

    return out_path, out_path, "Video created successfully."


def status_text():
    token_status = "Connected" if HF_TOKEN else "Not found. Run hf auth login."
    return f"Output folder: {OUTPUT_DIR}\nHugging Face token: {token_status}\nImage model: {IMAGE_MODEL}"


with gr.Blocks(title="AI Studio", css=CSS, theme=gr.themes.Soft()) as demo:
    gr.HTML(
        """
        <section id="hero">
            <h1>AI Studio</h1>
            <p>Professional AI content dashboard for image generation, screen recording, image-to-video creation, captions, music, and downloads.</p>
        </section>
        """
    )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### Prompt Builder")
            subject = gr.Textbox(label="Subject", placeholder="neon green Lamborghini in a luxury showroom")
            style = gr.Dropdown(
                ["Luxury car commercial", "Product ad", "Fashion editorial", "Travel reel", "Motivational short"],
                value="Luxury car commercial",
                label="Style",
            )
            build_btn = gr.Button("Build Prompt", variant="primary")
        with gr.Column(scale=1):
            gr.Markdown("### System Status")
            status = gr.Textbox(value=status_text(), lines=4, interactive=False, label="Status")

    prompt_box = gr.Textbox(label="Prompt", lines=4)
    caption_suggestion = gr.Textbox(label="Suggested Caption")

    build_btn.click(
        build_prompt,
        inputs=[subject, style],
        outputs=[prompt_box, caption_suggestion],
    )

    with gr.Tab("Text to Image"):
        gr.Markdown("Generate an image using Hugging Face.")
        generate_btn = gr.Button("Generate Image", variant="primary")
        generated_image = gr.Image(label="Generated Image", type="filepath")
        image_file = gr.File(label="Download Image")
        image_status = gr.Textbox(label="Result", interactive=False)

        generate_btn.click(
            generate_image,
            inputs=[prompt_box],
            outputs=[generated_image, image_file, image_status],
        )

    with gr.Tab("Image to Video"):
        gr.Markdown("Upload an image or use the generated image below to create a short video.")

        upload_image = gr.Image(label="Upload Image", type="filepath")

        with gr.Row():
            caption = gr.Textbox(label="Caption", value="This Looks Unreal")
            subtitle = gr.Textbox(label="Subtitle", value="Cinematic creator edit")
            brand = gr.Textbox(label="Brand Text", value="AI STUDIO")

        with gr.Row():
            aspect = gr.Dropdown(["9:16 Short", "16:9 Widescreen"], value="9:16 Short", label="Aspect Ratio")
            duration = gr.Slider(3, 12, value=6, step=1, label="Duration")
            fps = gr.Dropdown([12, 24], value=12, label="FPS")
            grade = gr.Dropdown(["Clean", "Cinematic", "Vibrant", "Moody"], value="Cinematic", label="Color Grade")
            music = gr.Dropdown(["None", "Chill", "Cinematic", "Upbeat"], value="Cinematic", label="Music")

        make_video_btn = gr.Button("Create Video From Uploaded Image", variant="primary")
        video = gr.Video(label="Preview Video")
        video_file = gr.File(label="Download Video")
        video_status = gr.Textbox(label="Result", interactive=False)

        make_video_btn.click(
            image_to_video,
            inputs=[upload_image, caption, subtitle, brand, aspect, duration, fps, grade, music],
            outputs=[video, video_file, video_status],
        )

    with gr.Tab("Generated Image to Video"):
        gr.Markdown("This uses the image created in the Text to Image tab.")

        gen_caption = gr.Textbox(label="Caption", value="Made With AI Studio")
        gen_subtitle = gr.Textbox(label="Subtitle", value="AI generated visual")
        gen_brand = gr.Textbox(label="Brand Text", value="AI STUDIO")

        with gr.Row():
            gen_aspect = gr.Dropdown(["9:16 Short", "16:9 Widescreen"], value="9:16 Short", label="Aspect Ratio")
            gen_duration = gr.Slider(3, 12, value=6, step=1, label="Duration")
            gen_fps = gr.Dropdown([12, 24], value=12, label="FPS")
            gen_grade = gr.Dropdown(["Clean", "Cinematic", "Vibrant", "Moody"], value="Vibrant", label="Color Grade")
            gen_music = gr.Dropdown(["None", "Chill", "Cinematic", "Upbeat"], value="Chill", label="Music")

        make_gen_video_btn = gr.Button("Create Video From Generated Image", variant="primary")
        gen_video = gr.Video(label="Preview Video")
        gen_video_file = gr.File(label="Download Video")
        gen_video_status = gr.Textbox(label="Result", interactive=False)

        make_gen_video_btn.click(
            image_to_video,
            inputs=[generated_image, gen_caption, gen_subtitle, gen_brand, gen_aspect, gen_duration, gen_fps, gen_grade, gen_music],
            outputs=[gen_video, gen_video_file, gen_video_status],
        )

    with gr.Tab("Screen Recording"):
        gr.Markdown("Screen recording runs inside this secure browser frame. Use Chrome or Edge.")
        gr.HTML(SCREEN_RECORDER)


if __name__ == "__main__":
    demo.launch()