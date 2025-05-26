import streamlit as st
import requests
import io
from PIL import Image
import datetime
import os

# --- Setup ---
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
style_presets = {
    "Realistic": "realistic photo, 8K UHD, DSLR",
    "Anime": "anime style, vibrant colors",
    "Oil Painting": "oil painting texture, brush strokes",
    "Cyberpunk": "neon lights, cyberpunk 2077 style"
}

st.set_page_config(page_title="AI Image Generator Pro", layout="wide")
st.title("🎨 AI Image Generator Pro")

# --- Sidebar Controls ---
st.sidebar.header("Settings")

# API Key
api_key = st.sidebar.text_input("🔑 Hugging Face API Key", type="password")
headers = {"Authorization": f"Bearer {api_key}"} if api_key else None

# Prompt
prompt = st.sidebar.text_area("🖊️ Enter your prompt:")

# Style Preset
style = st.sidebar.selectbox("🎨 Choose a style:", list(style_presets.keys()))

# Image Size
size_option = st.sidebar.selectbox("📐 Image Size:", ["512x512", "768x768"])
width, height = map(int, size_option.split("x"))

# Generate Button
generate = st.sidebar.button("✨ Generate Image")

# --- Image Output ---
if generate:
    if not api_key:
        st.error("Please enter your API key.")
    elif not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        full_prompt = f"{prompt.strip()}, {style_presets[style]}"
        payload = {
            "inputs": full_prompt,
            "parameters": {"width": width, "height": height}
        }

        with st.spinner("Generating image..."):
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=60)

                if response.status_code == 200:
                    image = Image.open(io.BytesIO(response.content))
                    st.image(image, caption="Generated Image", use_column_width=True)

                    # Save Option
                    os.makedirs("outputs", exist_ok=True)
                    filename = f"outputs/image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    image.save(filename)
                    st.success(f"✅ Image saved to: `{filename}`")
                else:
                    st.error(f"API Error {response.status_code}:\n{response.text}")

            except requests.Timeout:
                st.error("Request timed out. Try again.")
            except Exception as e:
                st.error(f"Failed to generate image:\n{e}")
