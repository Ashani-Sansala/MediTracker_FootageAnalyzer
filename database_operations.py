import mysql.connector
from config import config

def get_db_connection():
    return mysql.connector.connect(
        host=config.get("database_host"),
        user=config.get("database_user"),
        password=config.get("database_password"),
        database=config.get("database_name")
    )

def log_detection_to_db(cursor, eqp_id, cam_id, loc_id, frame_url, direction):
    sql = """INSERT INTO detectionLogs (eqpId, camId, locId, frameUrl, direction) 
             VALUES (%s, %s, %s, %s, %s)"""
    values = (eqp_id, cam_id, loc_id, frame_url, direction)
    cursor.execute(sql, values)
