import os
import cv2
import numpy as np
from pathlib import Path

def extract_frames(video_path,
                   output_dir,
                   hist_threshold=0.70,
                   min_area_ratio=0.25,
                   check_interval=20):

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    base_dir = Path(__file__).resolve().parent
    output_dir = base_dir / output_dir
    output_dir.mkdir(exist_ok=True, parents=True)

    cap = cv2.VideoCapture(video_path)

    prev_gray = None
    prev_hist = None
    frame_index = 0
    saved_count = 0
    frame_paths = []

    total_pixels = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        
        if frame_index % check_interval != 0:
            frame_index += 1
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        if prev_gray is None:
            prev_gray = gray
            total_pixels = gray.shape[0] * gray.shape[1]

            
            prev_hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            cv2.normalize(prev_hist, prev_hist)

            frame_path = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            saved_count += 1

            frame_index += 1
            continue

        
        curr_hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        cv2.normalize(curr_hist, curr_hist)

        hist_similarity = cv2.compareHist(
            prev_hist,
            curr_hist,
            cv2.HISTCMP_CORREL
        )

        
        if hist_similarity > hist_threshold:
            frame_index += 1
            continue

        
        diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

        changed_pixels = np.count_nonzero(thresh)
        area_ratio = changed_pixels / total_pixels

        
        if area_ratio > min_area_ratio:
            frame_path = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(frame_path, frame)
            frame_paths.append(frame_path)
            saved_count += 1

            prev_gray = gray
            prev_hist = curr_hist

        frame_index += 1

    cap.release()

    print(f"\nExtracted {saved_count} slide frames.")
    return frame_paths