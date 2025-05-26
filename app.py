import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import io
from PIL import Image, ImageTk
import datetime
import os
import json

class TextToImageGenerator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("AI Image Generator Pro")
        self.window.geometry("1100x750")
        
        # Initialize API configuration FIRST
        self.API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        self.headers = None
        self.api_key = None
        
        # Configuration
        self.config_file = "config.json"
        self.load_config()
        
        # Style presets
        self.style_presets = {
            "Realistic": "realistic photo, 8K UHD, DSLR",
            "Anime": "anime style, vibrant colors",
            "Oil Painting": "oil painting texture, brush strokes",
            "Cyberpunk": "neon lights, cyberpunk 2077 style"
        }
        
        self.create_widgets()

    def load_config(self):
        """Load API key from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key", "")
                    if self.api_key:
                        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        except Exception as e:
            print(f"Config load error: {e}")

    def save_config(self):
        """Save API key securely"""
        try:
            with open(self.config_file, "w") as f:
                json.dump({"api_key": self.api_key}, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")

    def create_widgets(self):
        # Control Panel (Left)
        control_frame = tk.Frame(self.window, width=300, bg="#f0f0f0", padx=10, pady=10)
        control_frame.pack(side="left", fill="y")

        # API Key Section
        api_frame = tk.LabelFrame(control_frame, text="API Settings", bg="#f0f0f0")
        api_frame.pack(fill="x", pady=5)
        
        self.api_btn = tk.Button(api_frame, 
                               text="Set API Key" if not self.api_key else "Update API Key",
                               command=self.set_api_key)
        self.api_btn.pack(pady=5)

        # Prompt Section
        tk.Label(control_frame, text="Prompt:", bg="#f0f0f0").pack(anchor="w")
        self.prompt_text = tk.Text(control_frame, height=8, width=35)
        self.prompt_text.pack(fill="x", pady=5)

        # Style Presets
        tk.Label(control_frame, text="Style Preset:", bg="#f0f0f0").pack(anchor="w")
        self.style_var = tk.StringVar(value="Realistic")
        ttk.Combobox(control_frame, 
                    textvariable=self.style_var,
                    values=list(self.style_presets.keys())).pack(fill="x", pady=5)

        # Image Size
        tk.Label(control_frame, text="Image Size:", bg="#f0f0f0").pack(anchor="w")
        self.size_var = tk.StringVar(value="512x512")
        ttk.Combobox(control_frame, 
                    textvariable=self.size_var,
                    values=["512x512", "768x768"]).pack(fill="x", pady=5)

        # Generate Button
        self.generate_btn = tk.Button(control_frame,
                                    text="Generate Image",
                                    command=self.generate_image,
                                    bg="#4CAF50",
                                    fg="white")
        self.generate_btn.pack(pady=15, fill="x")

        # Status
        self.status_var = tk.StringVar(value="Ready" if self.api_key else "Please set API Key")
        tk.Label(control_frame, 
               textvariable=self.status_var,
               bg="#f0f0f0").pack()

        # Image Display (Right)
        self.image_frame = tk.Frame(self.window)
        self.image_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.image_frame, bg="white")
        self.canvas.pack(expand=True, fill="both")
        
        # Save Button
        self.save_btn = tk.Button(self.image_frame,
                                text="Save Image",
                                command=self.save_image,
                                state="disabled")
        self.save_btn.pack(pady=10)

    def set_api_key(self):
        """Set new API key through secure dialog"""
        new_key = simpledialog.askstring("API Key", 
                                       "Enter Hugging Face API Key:",
                                       parent=self.window,
                                       show='*')
        if new_key:
            self.api_key = new_key
            self.headers = {"Authorization": f"Bearer {self.api_key}"}
            self.save_config()
            self.api_btn.config(text="Update API Key")
            self.status_var.set("Ready")
            messagebox.showinfo("Success", "API Key saved!")

    def generate_image(self):
        if not self.api_key:
            messagebox.showerror("Error", "Please set your API key first")
            return
            
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt")
            return

        # Add style preset to prompt
        full_prompt = f"{prompt}, {self.style_presets[self.style_var.get()]}"
        
        self.generate_btn.config(state="disabled")
        self.status_var.set("Generating... (20-40 seconds)")
        self.window.update()

        try:
            width, height = map(int, self.size_var.get().split('x'))
            payload = {
                "inputs": full_prompt,
                "parameters": {"width": width, "height": height}
            }
            
            response = requests.post(self.API_URL, 
                                  headers=self.headers, 
                                  json=payload,
                                  timeout=60)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                self.display_image(image)
                self.status_var.set("Generation complete!")
            else:
                messagebox.showerror("Error", 
                                    f"API Error {response.status_code}:\n{response.text}")
        except requests.Timeout:
            messagebox.showerror("Error", "Request timed out. Try again.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {str(e)}")
        finally:
            self.generate_btn.config(state="normal")

    def display_image(self, image):
        """Display generated image on canvas"""
        self.canvas.delete("all")
        
        # Calculate display dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        ratio = min(canvas_width/image.width, canvas_height/image.height)
        new_size = (int(image.width*ratio), int(image.height*ratio))
        image = image.resize(new_size, Image.LANCZOS)
        
        # Convert and display
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(canvas_width//2, canvas_height//2, 
                               image=self.tk_image, 
                               anchor="center")
        
        # Store original for saving
        self.current_image = image
        self.save_btn.config(state="normal")

    def save_image(self):
        """Save image to outputs folder"""
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"outputs/image_{timestamp}.png"
        try:
            self.current_image.save(filename)
            messagebox.showinfo("Saved", f"Image saved to:\n{os.path.abspath(filename)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    app = TextToImageGenerator()
    app.window.mainloop()