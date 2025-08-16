import os
import random
import time
from datetime import datetime, timedelta
from PIL import Image

def generate_test_images(folder, count, size=(100, 100), ext=".jpg"):
    os.makedirs(folder, exist_ok=True)
    now = datetime.now()
    for i in range(count):
        img = Image.new('RGB', size, color=(i % 256, (i*2) % 256, (i*3) % 256))
        file_path = os.path.join(folder, f"test_image_{i}{ext}")
        img.save(file_path)
        # Assign a random modification date within the last 365 days
        random_days = random.randint(0, 364)
        random_date = now - timedelta(days=random_days)
        mod_time = time.mktime(random_date.timetuple())
        os.utime(file_path, (mod_time, mod_time))

if __name__ == "__main__":
    # Example: Create 2000 jpg images for stress testing with random dates
    generate_test_images("test_stress_photos", 2000)
    print("Generated 2000 test images in 'test_stress_photos' folder with random dates.")
