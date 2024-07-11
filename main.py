import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import shutil
import threading
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
import cv2
import time
import mysql.connector

from config import config
from database_operations import get_db_connection, log_detection_to_db
from firebase_operations import upload_frame_to_firebase
from object_detection import perform_detection
from frame_processing import frame_producer, frame_consumer
from custom_utils import bbox_drawer, display_frames, drain_queue

def detection_worker(detection_queue, db_connection, running):
    cursor = db_connection.cursor()
    while running.is_set():
        try:
            task = detection_queue.get(timeout=1)
            if task is None:
                break
            eqp_id, cam_id, loc_id, frame, direction = task
            
            log_time = time.strftime("%Y%m%d-%H%M%S")
            frame_path = f'temp/{log_time}_{eqp_id}.png'
            cv2.imwrite(frame_path, frame)
            
            frame_url = upload_frame_to_firebase(frame_path, f'frame_logs/{log_time}_{eqp_id}.png')
            log_detection_to_db(cursor, eqp_id, cam_id, loc_id, frame_url, direction)
            
            print(f"Equipment {eqp_id} with direction {direction} detected")
            db_connection.commit()
        except Empty:
            if not running.is_set():
                break
            continue
        except Exception as e:
            print(f"Error in detection_worker: {e}")
            if not running.is_set():
                break
    cursor.close()
    
def extract_ids_from_path(video_path):
    filename = os.path.basename(video_path)
    parts = filename.split('_')
    cam_id = int(parts[0].replace('cam', ''))
    loc_id = int(parts[1].replace('loc', ''))

    return cam_id, loc_id

def main():
    print(f"\nWelcome to MediTracker Footage Analyzer")
    print(f"Analyzing...")
    local_video_path = config.get("local_video_path")
    cam_id, loc_id = extract_ids_from_path(local_video_path)
    
    # Create temporary directory
    temp_file = 'temp'
    if not os.path.exists(temp_file):
        os.makedirs(temp_file)
    
    # Initialize queues
    frame_queue = Queue(maxsize=30)
    detection_queue = Queue()
    draw_queue = Queue()
    display_queue = Queue()
    
    # Shared flag for thread coordination
    running = threading.Event()
    running.set()
    
    # Get database connection
    db_connection = get_db_connection()
    
    threads = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        threads.append(executor.submit(frame_producer, local_video_path, frame_queue, running))
        threads.append(executor.submit(frame_consumer, frame_queue, detection_queue, draw_queue, running, perform_detection, cam_id, loc_id))
        threads.append(executor.submit(bbox_drawer, draw_queue, display_queue, running))
        threads.append(executor.submit(detection_worker, detection_queue, db_connection, running))
        
        # Run display_frames in the main thread
        display_frames(display_queue, running)
        
        # Signal all threads to stop
        running.clear()
        
        # Drain queues
        drain_queue(frame_queue)
        drain_queue(detection_queue)
        drain_queue(draw_queue)
        drain_queue(display_queue)
        
        # Wait for all threads to complete
        for thread in threads:
            try:
                thread.result(timeout=10)  # Wait up to 10 seconds for each thread
            except Exception as e:
                print(f"Thread error: {e}")
    
    # Temp management
    if config.get("clear_temp"):
        shutil.rmtree(temp_file)
    
    # Close database connection
    try:
        db_connection.close()
    except mysql.connector.Error as err:
        print(f"Error closing database connection: {err}")

    print("Analysis finished!")

if __name__ == "__main__":
    main()
