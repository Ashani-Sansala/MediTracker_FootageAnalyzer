import firebase_admin
from firebase_admin import credentials, storage
from config import config

cred = credentials.Certificate(config.get("firebase_credentials_path"))
firebase_admin.initialize_app(cred, {'storageBucket': config.get("firebase_storage_bucket")})
bucket = storage.bucket()

def upload_frame_to_firebase(frame_path, destination_path):
    blob = bucket.blob(destination_path)
    blob.upload_from_filename(frame_path)
    blob.make_public()
    return blob.public_url
