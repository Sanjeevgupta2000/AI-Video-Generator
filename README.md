# AI Studio – Free AI Video Generator MVP

<div align="center">

🚀 AI-powered content creation app built with Python, Gradio, and Hugging Face

Create AI images, convert them into videos, add captions, background music, branding, and export short-form content — all in one place.

</div>

---

## 📌 Overview

AI Studio is a beginner-friendly AI Video Generator project designed to simplify AI-powered content creation.

The application allows users to:

- Generate AI images from text prompts
- Convert images into short videos
- Add captions and subtitles
- Add background music
- Apply branding/watermarks
- Export videos in social-media-ready formats

This project was built as a practical MVP (Minimum Viable Product) using free AI tools and open-source technologies.

---

## ✨ Features

### 🎨 AI Image Generation
- Generate AI images using text prompts
- Hugging Face inference integration
- Prompt builder support

### 🎬 AI Video Generation
- Convert generated images into animated videos
- Image-to-video workflow
- Export videos in MP4 format

### 📝 Captions & Branding
- Add subtitles/captions
- Overlay custom brand text
- Social-media-ready formatting

### 🎵 Background Music
- Add simple background music
- Enhance short-form video quality

### 📱 Multiple Video Formats
- Vertical 9:16 format for:
  - YouTube Shorts
  - Instagram Reels
  - TikTok

- Widescreen 16:9 format for YouTube videos

### 🎥 Recording & Preview
- Screen recording support
- Real-time preview
- Download generated images and videos

### 🎨 Visual Enhancements
- Basic color grading options
- Smooth transitions and effects

### ☁️ Free Deployment
- Deploy easily on Hugging Face Spaces
- Beginner-friendly setup

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core backend development |
| Gradio | Web interface |
| Hugging Face Hub | AI model integration |
| Pillow | Image processing |
| MoviePy | Video editing & rendering |
| NumPy | Numerical operations |
| imageio-ffmpeg | Video encoding |

---

## 📂 Project Structure

```text
AI-Studio/
│
├── app.py
├── requirements.txt
├── README.md
└── outputs/
```

---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/AI-Studio.git
cd AI-Studio
```

---

### 2️⃣ Create Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
HF_TOKEN=your_huggingface_token
```

Get your Hugging Face token from:

https://huggingface.co/settings/tokens

---

## ▶️ Run the Application

```bash
python app.py
```

After running the app, open the local Gradio URL in your browser.

Example:

```text
http://127.0.0.1:7860
```

---

## 📸 Workflow

1. Enter a text prompt
2. Generate an AI image
3. Convert image into video
4. Add captions/music/branding
5. Preview the output
6. Download final video

---

## 🚀 Deployment

You can deploy this project for free on:

- Hugging Face Spaces
- Render
- Railway

---

## 📦 Requirements

Example dependencies:

```txt
gradio
moviepy
pillow
numpy
huggingface_hub
imageio
imageio-ffmpeg
requests
```

---

## 🔮 Future Improvements

- Advanced AI video animation
- Voice-over generation
- AI avatars
- Automatic subtitle generation
- Multiple AI model support
- HD/4K export
- Scene transitions
- Timeline editor
- Cloud storage integration
- Multi-language support

---

## 🤝 Contributing

Contributions are welcome!

Steps to contribute:

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

Sanjeev Gupta

- BCA Graduate
- AI & Data Science Enthusiast
- Passionate about Generative AI and AI Applications

---

## ⭐ Support

If you found this project useful:

- Star the repository
- Share it with others
- Contribute to future improvements

---

<div align="center">

Made with ❤️ using Python & AI

</div>
