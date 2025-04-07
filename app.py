import gradio as gr
import zipfile
import os
import shutil
import uuid
import pandas as pd
from datetime import datetime, timedelta
from ultralytics import YOLO
from PIL import Image, ImageDraw
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenpyxlImage
import pytz
import zipfile


# Flask server details
SERVER_IP = "http://127.0.0.1:5000"  # Replace with actual EC2 IP
TEMP_FOLDER = "tmp"
PERSISTENT_FOLDER = "images"
OUTPUT_FOLDER = "output"

os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(PERSISTENT_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


model_path = "best.pt"
model = YOLO(model_path)

names1 = {0: 'Artwork', 1: 'Bar Stool', 2: 'Bench', 3: 'Bookcase - 2 Shelves', 4: 'Bookcase - 3 Shelves', 5: 'Bookcase - 4 Shelves', 6: 'Bookcase - 5- Shelves', 
7: 'Booth Seating - Complete Set', 8: 'Box of Electronics', 9: 'Box of Supplies', 10: 'Cafe Table', 11: 'CafeStacking Chair', 12: 'Cart - Mobile', 13: 'ChairFloor Mat', 14: 'Clock', 15: 'Coat Tree', 16: 'Coffee Maker', 17: 'Coffee Table', 18: 'Communal Table', 19: 'Computer Monitor', 20: 'Conference Chair', 21: 'Conference Phone', 22: 'Conference Table', 23: 'Cork Board', 24: 'Couch - Large', 25: 'Couch - Small', 26: 'Credenza', 27: 'Desk - 1PedDrawer', 28: 'Desk - 2PedDrawer', 29: 'Desk - L Shaped', 30: 'Desk - No Pedestals', 31: 'Desk - Reception', 32: 'Desk - U Shaped', 33: 'Desk Lamp', 34: 'Desk Phone - All-in-One', 35: 'Dishwasher', 36: 'Electrical BoardSmart Board', 37: 'Fan', 38: 'Filing - 2 Drawer Lateral', 39: 'Filing - 2 Drawer Vertical', 40: 'Filing - 3 Drawer Lateral', 41: 'Filing - 3 Drawer Vertical', 42: 'Filing - 4 Drawer Lateral', 43: 'Filing - 4 Drawer Vertical', 44: 'Filing - 5- Drawer Lateral', 45: 'Filing - 5- Drawer Vertical', 46: 'Floor Lamp', 47: 'Folding Table', 48: 'Footrest', 49: 'Garbage Can - Desk', 50: 'Garbage Can - Kitchen', 51: 'Gorilla Metal Racking', 52: 'GuestSide Chair -MetalPlastic-', 53: 'GuestSide Chair -Wood-', 54: 'Ice Maker', 55: 'Kettle', 56: 'Keyboard', 57: 'Laptop Computer', 58: 'Large Fridge - OversizedCommercial', 59: 'Large Storage Cabinet', 60: 'LecternPodium', 61: 'Lockers', 62: 'Lounge Chair', 63: 'Mail Cabinet Sorter', 64: 'Medium Storage Cabinet', 65: 'Microwave', 66: 'Mini Fridge', 67: 'Monitor Arms', 68: 'Mouse', 69: 'Paper Shredder', 70: 'Paper Tray', 71: 'Pedestal -Metal-', 72: 'Pedestal -Wood-', 73: 'Picture Frame', 74: 'Pillow', 75: 'Plant', 76: 'Plexi Glass Divider', 77: 'Printer - All-in-One', 78: 'Printer Table', 79: 'Privacy Screen', 80: 'Private Office Suite -ModernSteel-', 81: 'Private Office Suite -VintageWood-', 82: 'Projector', 83: 'Projector Screen', 84: 'Regular Fridge', 85: 'Safe', 86: 'Server Rack', 87: 'Side Table', 88: 'Sit-Stand Desk', 89: 'Small Storage Cabinet', 90: 'Space Heater', 91: 'Step Stool', 92: 'Tall -Metal- Cabinet', 93: 'Task Chair - no Arms', 94: 'Task Chair - with Arms', 95: 'Television Screen', 96: 'Toaster', 97: 'Toaster Oven', 98: 'Training Table', 99: 'Training Table - with Casters', 100: 'VariDesk', 101: 'Wall-Mounted Overhead', 102: 'Wardrobe', 103: 'Water Dispenser', 104: 'White Board', 105: 'Workstation - High', 106: 'Workstation - Low', 107: 'Workstation - Mid', 108: 'Workstation - Surface', 109: 'Workstation Panel', 110: 'desk return'}

def extract_images(zip_path, output_folder="tmp"):
    """Extract images from a zip file, placing all images in the temporary folder."""
    try:
        shutil.rmtree(TEMP_FOLDER)
    except Exception as e:
        print(f"Could not remove folder {TEMP_FOLDER}: {e}")
    os.makedirs(output_folder, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                zip_ref.extract(file, "temp_extracted")
    
    for root, _, files in os.walk("temp_extracted"):
        for file in files:
            src = os.path.join(root, file)
            dst = os.path.join(output_folder, file)
            shutil.move(src, dst)
    shutil.rmtree("temp_extracted")
    return output_folder

def zip_folder(folder_path, zip_name):
    zipf = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(folder_path):
        for file in files:
            zipf.write(os.path.join(root, file), file)
    zipf.close()

def run_yolo_on_images(image_folder):
    """Run YOLO on images and generate results with image download links."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    est = pytz.timezone('US/Eastern')
    timestamp = datetime.now(est).strftime("%Y-%m-%d_%H-%M-%S")    
    excel_filename = f"results_{timestamp}.xlsx"
    excel_path = os.path.join(OUTPUT_FOLDER, excel_filename)

    annotated_dir = os.path.join(PERSISTENT_FOLDER, f"annotated_{timestamp}")
    cropped_dir = os.path.join(PERSISTENT_FOLDER, f"cropped_{timestamp}")
    os.makedirs(annotated_dir, exist_ok=True)
    os.makedirs(cropped_dir, exist_ok=True)

    raw_zip = f"images_{timestamp}.zip"
    annotated_zip = f"annotated_{timestamp}.zip"
    cropped_zip = f"cropped_{timestamp}.zip"

    raw_zip_url = f'=HYPERLINK("{SERVER_IP}/download_raw_zip/{raw_zip}", "Raw ZIP")'
    annotated_zip_url = f'=HYPERLINK("{SERVER_IP}/download_annotated_zip/{annotated_zip}", "Annotated ZIP")'
    cropped_zip_url = f'=HYPERLINK("{SERVER_IP}/download_cropped_zip/{cropped_zip}", "Cropped ZIP")'

    wb = Workbook()
    ws = wb.active
    ws.append(["Item Name", "Confidence", "Annotated Image", "Cropped Object", "Raw Image Name", "Cropped Image Name", "Annotated Image Name", "Raw Zip", "Cropped Zip", "Annotated Zip"])
    ws.column_dimensions["C"].width = 100
    ws.column_dimensions["D"].width = 100

    # Get the list of image paths from the temporary folder
    image_paths = [
        os.path.join(image_folder, img)
        for img in os.listdir(image_folder)
        if img.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    results = model(image_paths)

    for img_path, result in zip(image_paths, results):
        print(image_paths)
        image = Image.open(img_path)
        draw = ImageDraw.Draw(image)
        base_name = os.path.basename(img_path)

        # Generate annotated image
        annotated_path = os.path.join(annotated_dir, "annotated_" + base_name)
        result.save(annotated_path)
        first_row = True
        for i, box in enumerate(result.boxes):
            xyxy = box.xyxy[0].tolist()
            conf = float(box.conf[0].item())
            if conf < 0.55:
                continue
            conf = int(conf * 100)
            class_id = int(box.cls[0].item())
            item_name = f"{names1[class_id]}"
            
            # Crop object
            cropped_obj = image.crop(xyxy)
            cropped_path = os.path.join(cropped_dir, f"cropped_{item_name}_{i}.jpg")
            cropped_obj.save(cropped_path)
            
            # Insert row data
            row_data = [item_name, conf, None, None, base_name, f"cropped_{item_name}_{i}.jpg", f"annotated_{base_name}"]
            if first_row:
                row_data.extend([raw_zip_url, cropped_zip_url, annotated_zip_url])
                first_row = False
            else:
                row_data.extend(["", "", ""])

            ws.append(row_data)

            # Insert images into Excel
            img_annotated = OpenpyxlImage(annotated_path)
            img_cropped = OpenpyxlImage(cropped_path)

            img_annotated.width, img_annotated.height = 200, 200
            img_cropped.width, img_cropped.height = 200, 200

            row_num = ws.max_row
            ws.row_dimensions[row_num].height = 200
            ws.add_image(img_annotated, f"C{row_num}")
            ws.add_image(img_cropped, f"D{row_num}")

    zip_folder(image_folder, os.path.join(PERSISTENT_FOLDER, raw_zip))
    zip_folder(annotated_dir, os.path.join(PERSISTENT_FOLDER, annotated_zip))
    zip_folder(cropped_dir, os.path.join(PERSISTENT_FOLDER, cropped_zip))

    # Save Excel file
    wb.save(excel_path)
    shutil.rmtree(annotated_dir)
    shutil.rmtree(cropped_dir)
    return excel_path

def process_zip(zip_file):
    image_paths = extract_images(zip_file)
    excel_file = run_yolo_on_images(image_paths)
    return excel_file

iface = gr.Interface(
    fn=process_zip,
    inputs=gr.File(type="filepath", label="Upload Zip File"),
    outputs=gr.File()
)

iface.launch(server_name="0.0.0.0",server_port=7860)
