from ultralytics import YOLO

model = YOLO("best.pt")

results = model("images")

for result in results:
    print(result)