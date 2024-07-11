import cv2
from queue import Empty
from config import config
from collections import deque

def frame_producer(video_path, frame_queue, running):
    cap = cv2.VideoCapture(video_path)
    frame_skip = config.get("frame_skip")
    frame_width = config.get("frame_width", 0)
    frame_height = config.get("frame_height", 0)
    
    while running.is_set() and cap.isOpened():
        for _ in range(frame_skip):
            cap.read()
        ret, frame = cap.read()
        if not ret:
            break
        
        if (frame_width != 0) and (frame_height != 0):
            frame = cv2.resize(frame, (frame_width, frame_height))
        
        frame_queue.put(frame)
        
        if not running.is_set():
            break
    
    cap.release()
    frame_queue.put(None)  # Signal end of frames

def frame_consumer(frame_queue, detection_queue, draw_queue, running, object_detection, cam_id, loc_id):
    direction_buffer = {}
    logged_objects = deque(maxlen=1000)
    buffer_size = config.get("buffer_size")
    min_frames_for_logging = config.get("min_frames_for_logging")
    movement_threshold = config.get("movement_threshold")

    while running.is_set():
        try:
            frame = frame_queue.get(timeout=1)
            if frame is None:
                break
        except Empty:
            if not running.is_set():
                break
            continue

        bboxes, confidences, class_ids, class_names = object_detection(frame)
        draw_queue.put((frame.copy(), bboxes, confidences, class_ids, class_names))

        detected_equipment = {}

        for bbox, class_id in zip(bboxes, class_ids):
            object_id = f"{class_id}_{len(detected_equipment.get(class_id, []))}"
            detected_equipment.setdefault(class_id, []).append(object_id)
            
            current_position = ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)
            
            direction_buffer.setdefault(object_id, []).append(current_position)
            direction_buffer[object_id] = direction_buffer[object_id][-buffer_size:]
            
            if len(direction_buffer[object_id]) >= min_frames_for_logging:
                first_pos = direction_buffer[object_id][0]
                last_pos = direction_buffer[object_id][-1]
                dx, dy = last_pos[0] - first_pos[0], last_pos[1] - first_pos[1]
                
                if abs(dx) > movement_threshold or abs(dy) > movement_threshold:
                    direction = 'Right' if dx > 0 else 'Left' if abs(dx) > abs(dy) else 'In' if dy > 0 else 'Out'
                else:
                    direction = 'Static'
                
                if object_id not in logged_objects:
                    eqp_id = config.get("classes")[str(int(class_id))]
                    detection_queue.put((eqp_id, cam_id, loc_id, frame.copy(), direction))
                    logged_objects.append(object_id)

        current_objects = set().union(*detected_equipment.values())
        for object_id in list(direction_buffer.keys()):
            if object_id not in current_objects:
                del direction_buffer[object_id]
                
        # For debugging
        """
        print("current_objects:- ", current_objects)
        print("Detected_equipment:- ", detected_equipment)
        print("Logged_objects:- ", logged_objects)
        print("Direction_buffer:- ", direction_buffer)
        """
        
    detection_queue.put(None)
    draw_queue.put(None)
