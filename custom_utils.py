import cv2
from queue import Empty
from config import config

def draw_bboxes(image, bboxes, confidences, class_ids, class_names):
    for bbox, conf, class_id in zip(bboxes, confidences, class_ids):
        x1, y1, x2, y2 = map(int, bbox)
        label = f"{class_names[int(class_id)]} {conf:.2f}"
        cv2.rectangle(image, (x1, y1), (x2, y2), color=(255, 0, 0), thickness=2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

def bbox_drawer(draw_queue, display_queue, running):
    while running.is_set():
        try:
            task = draw_queue.get(timeout=1)
            if task is None:
                break
            frame, bboxes, confidences, class_ids, class_names = task
            draw_bboxes(frame, bboxes, confidences, class_ids, class_names)
            display_queue.put(frame)
        except Empty:
            if not running.is_set():
                break
            continue

    display_queue.put(None)  # Signal end of frames

def display_frames(display_queue, running):
    while running.is_set():
        try:
            frame = display_queue.get(timeout=1)
            if frame is None:
                break
            
            if config.get("enable_preview", False):
                cv2.imshow('Object Detection', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    running.clear()  # Signal to stop all threads
                    print("'q' pressed, signaling threads to stop")
                    break
                
        except Empty:
            continue

    cv2.destroyAllWindows()

def drain_queue(q):
    while not q.empty():
        try:
            q.get_nowait()
        except Empty:
            break
