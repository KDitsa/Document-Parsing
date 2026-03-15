import cv2
import numpy as np
import os
from skimage.metrics import structural_similarity as ssim
from pathlib import Path

def get_content_score(frame):
    try:
        small = cv2.resize(frame, (640, 360))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return np.sum(edges) / 255
    except Exception as e:
        print("Content score error:", e)
        return 0


def process_chunk(cap, start_frame, end_frame, fps, skip_frames):

    candidates = []

    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        prev_frame_gray = None
        frame_id = start_frame

        while frame_id < end_frame:

            try:
                ret, frame = cap.read()
                if not ret:
                    break
            except Exception as e:
                print("Frame read error:", e)
                break

            for _ in range(skip_frames - 1):
                if frame_id >= end_frame:
                    break
                cap.grab()
                frame_id += 1

            frame_id += 1

            try:
                small_analysis = cv2.resize(frame, (320, 180))
                gray = cv2.cvtColor(small_analysis, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (15, 15), 0)
            except Exception as e:
                print("Frame preprocessing error:", e)
                continue

            if prev_frame_gray is not None:

                diff = cv2.absdiff(prev_frame_gray, gray)
                motion = np.mean(diff)

                if motion < 1.0:
                    content = get_content_score(frame)

                    candidates.append({
                        "frame": frame.copy(),
                        "score": content,
                        "time": frame_id / fps
                    })

            prev_frame_gray = gray

    except Exception as e:
        print("Chunk processing error:", e)

    return candidates


def get_histogram(frame):

    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        hist = cv2.calcHist([gray], [0], None, [256], [0,256])
        hist = cv2.normalize(hist, hist).flatten()

        return hist
    except Exception as e:
        print("Histogram error:", e)
        return None


def group_slides_histogram(candidates, fps, similarity_threshold=0.9):

    try:

        if not candidates:
            return []

        final_slides = []

        prev_hist = get_histogram(candidates[0]["frame"])
        current_group = [candidates[0]]

        for i in range(1, len(candidates)):

            curr_hist = get_histogram(candidates[i]["frame"])

            if curr_hist is None or prev_hist is None:
                continue

            similarity = cv2.compareHist(prev_hist, curr_hist, cv2.HISTCMP_CORREL)

            if similarity > similarity_threshold:
                current_group.append(candidates[i])
            else:
                best = max(current_group, key=lambda x: x["score"])
                final_slides.append(best)

                current_group = [candidates[i]]

            prev_hist = curr_hist

        final_slides.append(max(current_group, key=lambda x: x["score"]))

        return final_slides

    except Exception as e:
        print("Grouping error:", e)
        return []


def extract_slides_chunked(video_path,
                           output_folder,
                           chunk_seconds=5):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    frame_paths = []

    try:
        base_dir = Path(__file__).resolve().parent
        output_folder = base_dir / output_folder
        output_folder.mkdir(exist_ok=True, parents=True)
        
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise IOError("Cannot open video file")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        skip_frames = int(fps / 4)
        chunk_size = int(chunk_seconds * fps)

        saved = 0
        last_saved_gray = None

        print(f"Total frames: {total_frames}")
        print(f"Processing in {chunk_seconds}s chunks\n")

        for start in range(0, total_frames, chunk_size):

            end = min(start + chunk_size, total_frames)

            print(f"Processing frames {start} → {end}")

            try:
                candidates = process_chunk(cap, start, end, fps, skip_frames)
                slides = group_slides_histogram(candidates, fps)
            except Exception as e:
                print("Chunk error:", e)
                continue

            if slides:

                scores = [s["score"] for s in slides]
                median_score = np.median(scores)
                adaptive_thresh = median_score * 0.4

                for slide in slides:

                    try:
                        if slide["score"] >= adaptive_thresh:

                            gray = cv2.cvtColor(slide["frame"], cv2.COLOR_BGR2GRAY)

                            if last_saved_gray is not None:
                                similarity = ssim(last_saved_gray, gray)
                                if similarity > 0.92:
                                    continue

                            filename = os.path.join(
                                output_folder,
                                f"slide_{saved:04d}.jpg"
                            )

                            cv2.imwrite(filename, slide["frame"])
                            frame_paths.append(filename)

                            last_saved_gray = gray
                            saved += 1

                    except Exception as e:
                        print("Slide save error:", e)

        cap.release()

        print(f"\nTotal slides saved: {saved}")

    except Exception as e:
        print("Extraction error:", e)

    return frame_paths
