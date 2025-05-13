import os
from tkinter import Tk, Label, Button, filedialog, StringVar, OptionMenu, Entry
from PIL import Image

# === Preset ขนาดภาพ Facebook ===
preset_sizes = {
    "Profile Picture (600x600)": (600, 600),
    "Cover Page (1640x924)": (1640, 924),
    "Cover Group (1200x628)": (1200, 628),
    "Cover Event (1640x628)": (1640, 628),
    "Story (1080x1920)": (1080, 1920),
    "Timeline Vertical (1200x1500)": (1200, 1500),
    "Timeline Square (1200x1200)": (1200, 1200),
    "Timeline Horizontal (1200x675)": (1200, 675)
}

# === ฟังก์ชันหลัก ===
def process_images():
    quality = quality_entry.get()
    try:
        quality = int(quality)
        if not (1 <= quality <= 100):
            raise ValueError
    except ValueError:
        status_label.config(text="❌ Enter a valid quality (1-100)")
        return

    if not selected_files:
        status_label.config(text="❌ Please select image files first")
        return

    size = preset_sizes[preset_var.get()]
    output_folder_resized = os.path.join("output", "resized")
    output_folder_compressed = os.path.join("output", "compressed")
    os.makedirs(output_folder_resized, exist_ok=True)
    os.makedirs(output_folder_compressed, exist_ok=True)

    for file_path in selected_files:
        try:
            image = Image.open(file_path)
            file_name = os.path.basename(file_path)
            file_root, file_ext = os.path.splitext(file_name)

            # === 1. Resize แล้วเซฟใน /output/resized/
            resized_image = image.resize(size)
            resized_path = os.path.join(output_folder_resized, f"{file_root}_resized{file_ext}")
            resized_image.save(resized_path)
            print(f"✅ Resized saved: {resized_path}")

            # === 2. ลดคุณภาพ แล้วเซฟใน /output/compressed/
            compressed_image = image.convert("RGB")
            compressed_path = os.path.join(output_folder_compressed, f"{file_root}_compressed.jpg")
            compressed_image.save(compressed_path, quality=quality)
            print(f"✅ Compressed saved: {compressed_path}")

        except Exception as e:
            status_label.config(text=f"❌ Error: {e}")
            return

    status_label.config(text="✅ Done! Files saved in output/resized/ and output/compressed/")

def browse_files():
    global selected_files
    selected_files = filedialog.askopenfilenames(
        title="Select Images",
        filetypes=[("Image Files", "*.jpg *.jpeg *.png")]
    )
    file_label.config(text=f"{len(selected_files)} file(s) selected")

# === GUI Layout ===
app = Tk()
app.title("Facebook Image Resizer & Compressor")
app.geometry("420x310")

Label(app, text="📐 Choose Facebook Size:").pack()
preset_var = StringVar(app)
preset_var.set("Story (1080x1920)")
OptionMenu(app, preset_var, *preset_sizes.keys()).pack()

Label(app, text="🧪 Enter JPEG Quality (1-100):").pack()
quality_entry = Entry(app)
quality_entry.insert(0, "30")
quality_entry.pack()

Button(app, text="📂 Select Images", command=browse_files).pack(pady=5)
file_label = Label(app, text="No file selected")
file_label.pack()

Button(app, text="🚀 Process Images", command=process_images).pack(pady=10)
status_label = Label(app, text="")
status_label.pack()

app.mainloop()
