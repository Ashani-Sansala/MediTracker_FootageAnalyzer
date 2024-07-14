# MediTracker Footage Analyzer

## Overview

MediTracker Footage Analyzer is a system designed to analyze video footage in medical environments. It automatically detects and tracks medical equipment, logging their movements in real-time. This tool is part of a larger system that updates equipment locations on a dashboard. Here are the links to the related repositories:

- Frontend: https://github.com/Ashani-Sansala/MediTrack_System_Frontend
- Backend: https://github.com/Ashani-Sansala/MediTrack_System_Backend

## Features

- Real-time detection of hospital equipment using YOLOv5
- Movement tracking and direction analysis
- Integration with MySQL database for logging detections
- Firebase integration for storing and sharing detected frames
- Configurable parameters for optimizing performance and accuracy

## Requirements

- Python 3.10 or higher (recommended)
- CUDA-capable GPU (recommended for faster processing)
- Sufficient storage for video files and temporary data

## Installation

1. Clone the repository:

```
https://github.com/Ashani-Sansala/MediTracker_FootageAnalyzer.git
cd MediTracker_FootageAnalyzer
```

2. Install required dependencies:

```
pip install -r requirements.txt
```

3. Ensure you have the necessary credentials for MySQL database and Firebase.

## Configuration

Before running the analyzer, configure the `config.json` file. Open it in a text editor and set the following parameters:

- Database Settings (MySQL)
- Firebase Settings
- Video Processing Settings

Refer to the user manual for detailed explanations of each parameter.

## Usage

1. Ensure the backend system is running:
   - The MediTracker Footage Analyzer depends on a backend system for database and storage operations.
   - Make sure the backend is set up and running before proceeding.

2. Prepare your video footage files:
- Name format: `camX_locY_Z.mp4` (X: Camera ID, Y: Location ID, Z: Footage number/name)
- Place the video file in the directory specified by `local_video_path` in `config.json`.

3. Run the main script:

```
python main.py
```

4. The system will start analyzing the video footage file specified in `config.json`.

Note: It's crucial to have the backend system operational before running the Footage Analyzer. The analyzer relies on the backend for database connections.

## Monitoring Progress

- If `enable_preview` is set to true, a window will show the video with detection boxes.
- The console will display messages about detected equipment and their movements.

## Viewing Results

- Detection logs are stored in the MySQL database specified in `config.json`.
- Frames with detected equipment are uploaded to Firebase Storage.

## Performance Optimization

Refer to the user manual for detailed information on optimizing performance through configuration parameters such as:

- Frame skip
- Frame resizing
- Confidence threshold
- Buffer size
- Movement threshold

## Troubleshooting

If you encounter issues:

- Verify all paths in `config.json` are correct and accessible.
- Check database and Firebase credentials.
- For detection inaccuracies, adjust `confidence_threshold` or use a better-trained model.
- For performance issues, try increasing `frame_skip` or reducing `frame_width` and `frame_height`.
