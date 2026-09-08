import os


image_dir = "static/images/logos"

for filename in os.listdir(image_dir):

    if filename.lower().endswith(('.png')):

        new_name = filename.replace(" ", "_")
        old_path = os.path.join(image_dir, filename)
        new_path = os.path.join(image_dir, new_name)
        
        os.rename(old_path, new_path)
        print(f"Preimenovano: {filename} -> {new_name}")