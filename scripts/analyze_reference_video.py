#!/usr/bin/env python3
"""Analyze visual rhythm and style metrics for the reference video."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
VIDEO_PATH = ROOT / "research" / "Ted-How-to-play-a-Rubik-s.mp4"
ADAPTIVE_SCENES_PATH = ROOT / "research" / "reference_scenes_adaptive.csv"
CONTENT_SCENES_PATH = ROOT / "research" / "reference_scenes_content.csv"
FRAME_METRICS_PATH = ROOT / "research" / "opencv_frame_metrics_1fps.csv"
SCENE_METRICS_PATH = ROOT / "research" / "opencv_scene_metrics_adaptive.csv"
SUMMARY_PATH = ROOT / "research" / "opencv_visual_summary.json"
CHART_PATH = ROOT / "research" / "opencv_visual_metrics_chart.jpg"


def parse_timecode(value: str) -> float:
    hours, minutes, seconds = value.strip().split(":")
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def format_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    rest = seconds - minutes * 60
    return f"{minutes:02d}:{rest:06.3f}"


def read_scene_csv(path: Path) -> list[dict[str, float | int | str]]:
    scenes: list[dict[str, float | int | str]] = []
    with path.open(newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    header_index = None
    for index, row in enumerate(rows):
        if row and row[0].strip() == "Scene Number":
            header_index = index
            break

    if header_index is None:
        raise RuntimeError(f"Could not find scene table in {path}")

    headers = [cell.strip() for cell in rows[header_index]]
    for row in rows[header_index + 1 :]:
        if not row or len(row) < len(headers):
            continue
        data = dict(zip(headers, [cell.strip() for cell in row]))
        if not data.get("Scene Number"):
            continue
        start_seconds = parse_timecode(data["Start Timecode"])
        end_seconds = parse_timecode(data["End Timecode"])
        scenes.append(
            {
                "scene": int(data["Scene Number"]),
                "start_seconds": start_seconds,
                "end_seconds": end_seconds,
                "duration_seconds": end_seconds - start_seconds,
                "start_time": data["Start Timecode"],
                "end_time": data["End Timecode"],
            }
        )
    return scenes


def hue_name(hue_degrees: float) -> str:
    if hue_degrees < 15 or hue_degrees >= 345:
        return "red"
    if hue_degrees < 45:
        return "orange"
    if hue_degrees < 75:
        return "yellow"
    if hue_degrees < 165:
        return "green/cyan"
    if hue_degrees < 255:
        return "blue"
    if hue_degrees < 315:
        return "magenta"
    return "red/magenta"


def frame_metrics(frame: np.ndarray, previous_gray: np.ndarray | None) -> tuple[dict[str, float], np.ndarray]:
    small = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 160)

    hue = hsv[:, :, 0].astype(np.float32) * 2.0
    saturation = hsv[:, :, 1].astype(np.float32) / 255.0
    value = hsv[:, :, 2].astype(np.float32) / 255.0

    if previous_gray is None:
        motion = 0.0
    else:
        motion = float(np.mean(cv2.absdiff(gray, previous_gray)) / 255.0)

    metrics = {
        "hue_degrees": float(np.mean(hue)),
        "saturation": float(np.mean(saturation)),
        "brightness": float(np.mean(value)),
        "contrast": float(np.std(gray) / 255.0),
        "edge_density": float(np.mean(edges > 0)),
        "motion_energy": motion,
    }
    return metrics, gray


def collect_frame_metrics() -> tuple[list[dict[str, float | str]], dict[str, float]]:
    cap = cv2.VideoCapture(str(VIDEO_PATH))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {VIDEO_PATH}")

    fps = float(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    rows: list[dict[str, float | str]] = []
    previous_gray = None
    second = 0
    while second < math.floor(duration):
        cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        metrics, previous_gray = frame_metrics(frame, previous_gray)
        rows.append(
            {
                "time_seconds": float(second),
                "timecode": format_time(second),
                **metrics,
                "dominant_hue_family": hue_name(metrics["hue_degrees"]),
            }
        )
        second += 1

    cap.release()
    return rows, {"fps": fps, "total_frames": total_frames, "duration_seconds": duration}


def aggregate_scene_metrics(
    frame_rows: list[dict[str, float | str]], scenes: list[dict[str, float | int | str]]
) -> list[dict[str, float | int | str]]:
    numeric_fields = [
        "hue_degrees",
        "saturation",
        "brightness",
        "contrast",
        "edge_density",
        "motion_energy",
    ]
    result: list[dict[str, float | int | str]] = []

    for scene in scenes:
        start = float(scene["start_seconds"])
        end = float(scene["end_seconds"])
        members = [
            row
            for row in frame_rows
            if start <= float(row["time_seconds"]) < end
        ]
        if not members:
            continue
        averages = {
            field: float(np.mean([float(row[field]) for row in members]))
            for field in numeric_fields
        }
        hue_counts: dict[str, int] = {}
        for row in members:
            family = str(row["dominant_hue_family"])
            hue_counts[family] = hue_counts.get(family, 0) + 1
        dominant_family = max(hue_counts.items(), key=lambda item: item[1])[0]
        result.append(
            {
                "scene": int(scene["scene"]),
                "start_time": str(scene["start_time"]),
                "end_time": str(scene["end_time"]),
                "duration_seconds": round(float(scene["duration_seconds"]), 3),
                "sampled_seconds": len(members),
                **{field: round(value, 4) for field, value in averages.items()},
                "dominant_hue_family": dominant_family,
            }
        )
    return result


def write_csv(path: Path, rows: list[dict[str, float | int | str]]) -> None:
    if not rows:
        return
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def draw_chart(rows: list[dict[str, float | str]]) -> None:
    width = 1400
    height = 640
    margin_left = 70
    margin_right = 30
    margin_top = 50
    panel_height = 135
    chart = np.full((height, width, 3), 245, dtype=np.uint8)

    series = [
        ("brightness", (50, 80, 200), "brightness"),
        ("saturation", (60, 160, 80), "saturation"),
        ("edge_density", (200, 90, 50), "edge density"),
        ("motion_energy", (160, 60, 180), "motion energy"),
    ]

    max_time = max(float(row["time_seconds"]) for row in rows) or 1.0
    plot_width = width - margin_left - margin_right

    for panel_index, (field, color, label) in enumerate(series):
        y0 = margin_top + panel_index * panel_height
        y1 = y0 + panel_height - 35
        cv2.putText(chart, label, (20, y0 + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (35, 35, 35), 2)
        cv2.line(chart, (margin_left, y1), (width - margin_right, y1), (210, 210, 210), 1)
        cv2.line(chart, (margin_left, y0), (margin_left, y1), (210, 210, 210), 1)
        values = [float(row[field]) for row in rows]
        max_value = max(values) or 1.0
        if field in {"brightness", "saturation"}:
            max_value = 1.0
        points = []
        for row, value in zip(rows, values):
            x = margin_left + int(float(row["time_seconds"]) / max_time * plot_width)
            y = y1 - int((value / max_value) * (y1 - y0))
            points.append((x, y))
        for left, right in zip(points, points[1:]):
            cv2.line(chart, left, right, color, 2)

    for tick in range(0, int(max_time) + 1, 30):
        x = margin_left + int(tick / max_time * plot_width)
        cv2.line(chart, (x, height - 45), (x, height - 35), (120, 120, 120), 1)
        cv2.putText(chart, f"{tick}s", (x - 16, height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (80, 80, 80), 1)

    cv2.imwrite(str(CHART_PATH), chart)


def main() -> None:
    adaptive_scenes = read_scene_csv(ADAPTIVE_SCENES_PATH)
    content_scenes = read_scene_csv(CONTENT_SCENES_PATH)
    frame_rows, metadata = collect_frame_metrics()
    scene_rows = aggregate_scene_metrics(frame_rows, adaptive_scenes)

    write_csv(FRAME_METRICS_PATH, frame_rows)
    write_csv(SCENE_METRICS_PATH, scene_rows)
    draw_chart(frame_rows)

    summary = {
        "video": metadata,
        "py_scene_detect": {
            "content_scene_count": len(content_scenes),
            "content_average_scene_length": round(metadata["duration_seconds"] / len(content_scenes), 3),
            "adaptive_scene_count": len(adaptive_scenes),
            "adaptive_average_scene_length": round(metadata["duration_seconds"] / len(adaptive_scenes), 3),
            "content_cut_times": [scene["start_time"] for scene in content_scenes[1:]],
            "adaptive_cut_times": [scene["start_time"] for scene in adaptive_scenes[1:]],
        },
        "opencv": {
            "sampled_seconds": len(frame_rows),
            "mean_brightness": round(float(np.mean([float(row["brightness"]) for row in frame_rows])), 4),
            "mean_saturation": round(float(np.mean([float(row["saturation"]) for row in frame_rows])), 4),
            "mean_edge_density": round(float(np.mean([float(row["edge_density"]) for row in frame_rows])), 4),
            "mean_motion_energy": round(float(np.mean([float(row["motion_energy"]) for row in frame_rows])), 4),
            "highest_motion_seconds": [
                {
                    "timecode": row["timecode"],
                    "motion_energy": round(float(row["motion_energy"]), 4),
                    "dominant_hue_family": row["dominant_hue_family"],
                }
                for row in sorted(frame_rows, key=lambda row: float(row["motion_energy"]), reverse=True)[:10]
            ],
            "scene_metrics_file": str(SCENE_METRICS_PATH.relative_to(ROOT)),
            "frame_metrics_file": str(FRAME_METRICS_PATH.relative_to(ROOT)),
            "chart_file": str(CHART_PATH.relative_to(ROOT)),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
