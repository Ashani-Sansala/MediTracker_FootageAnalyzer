import torch
import cv2
from config import config

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = torch.hub.load('ultralytics/yolov5', 'custom', path=config.get("model_path")).to(device)

def perform_detection(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = model(frame_rgb)
    
    bboxes = results.xyxy[0][:, :4].cpu().numpy()
    confidences = results.xyxy[0][:, 4].cpu().numpy()
    class_ids = results.xyxy[0][:, 5].cpu().numpy()
    
    valid_indices = confidences >= config.get("confidence_threshold")
    return bboxes[valid_indices], confidences[valid_indices], class_ids[valid_indices], results.names
