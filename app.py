import streamlit as st
import requests
from PIL import Image
import io
import datetime
import os
from huggingface_hub import InferenceClient

# Page configuration
st.set_page_config(
    page_title="AI Image Generator Pro",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextArea textarea {
        min-height: 150px;
    }
    .stSelectbox, .stTextInput {
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_image' not in st.session_state:
    st.session_state.generated_image = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Style presets
STYLE_PRESETS = {
    "Realistic": "realistic photo, 8K UHD, DSLR",
    "Anime": "anime style, vibrant colors",
    "Oil Painting": "oil painting texture, brush strokes",
    "Cyberpunk": "neon lights, cyberpunk 2077 style"
}

# Main function
def main():
    st.title("🎨 AI Image Generator Pro")
    
    with st.sidebar:
        st.header("Settings")
        
        # API Key Management
        api_key = st.text_input(
            "Hugging Face API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get your key from https://huggingface.co/settings/tokens"
        )
        
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
            st.rerun()
        
        # Model selection
        model_name = st.selectbox(
            "Model",
            ["stabilityai/stable-diffusion-xl-base-1.0", 
             "runwayml/stable-diffusion-v1-5"],
            index=0
        )
        
        # Style preset
        style = st.selectbox(
            "Style Preset",
            list(STYLE_PRESETS.keys()),
            index=0
        )
        
        # Image size
        size = st.selectbox(
            "Image Size",
            ["512x512", "768x768"],
            index=0
        )
    
    # Prompt input
    prompt = st.text_area(
        "Enter your prompt:",
        placeholder="A beautiful landscape with mountains and rivers...",
        height=150
    )
    
    # Generate button
    if st.button("Generate Image", use_container_width=True):
        if not st.session_state.api_key:
            st.error("Please enter your Hugging Face API key")
            return
        if not prompt:
            st.error("Please enter a prompt")
            return
            
        generate_image(prompt, style, size, model_name)
    
    # Display generated image
    if st.session_state.generated_image:
        st.image(st.session_state.generated_image, use_column_width=True)
        
        # Save/download options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save to Gallery"):
                save_image()
        with col2:
            download_image()

def generate_image(prompt, style, size, model_name):
    """Generate image using Hugging Face API"""
    full_prompt = f"{prompt}, {STYLE_PRESETS[style]}"
    width, height = map(int, size.split('x'))
    
    with st.spinner(f"Generating image... (This may take 20-40 seconds)"):
        try:
            client = InferenceClient(token=st.session_state.api_key)
            image = client.text_to_image(
                prompt=full_prompt,
                model=model_name,
                width=width,
                height=height
            )
            
            st.session_state.generated_image = image
            st.success("Image generated successfully!")
            
        except Exception as e:
            st.error(f"Generation failed: {str(e)}")

def save_image():
    """Save image to local directory"""
    os.makedirs("generated_images", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated_images/image_{timestamp}.png"
    
    try:
        st.session_state.generated_image.save(filename)
        st.success(f"Image saved to {os.path.abspath(filename)}")
    except Exception as e:
        st.error(f"Failed to save image: {str(e)}")

def download_image():
    """Create download button for image"""
    img_bytes = io.BytesIO()
    st.session_state.generated_image.save(img_bytes, format="PNG")
    st.download_button(
        label="Download Image",
        data=img_bytes.getvalue(),
        file_name=f"ai_generated_{datetime.datetime.now().strftime('%Y%m%d')}.png",
        mime="image/png"
    )

if __name__ == "__main__":
    main()