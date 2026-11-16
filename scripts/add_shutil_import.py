file_path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\pdf_archive_service.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

target = "import os\n"
replacement = "import os\nimport shutil\n"

text = text.replace(target, replacement, 1)
with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Added import shutil successfully!")
