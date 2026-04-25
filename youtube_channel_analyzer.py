"""
YouTube Channel Analyzer
Fetches all videos from a channel and exports title, views, and publish date to CSV.

Usage:
    python youtube_channel_analyzer.py --channel @nateliason --api_key YOUR_KEY
    python youtube_channel_analyzer.py --channel UCaggiu76cPdLduA8R2lCSQA --api_key YOUR_KEY

Requirements:
    pip install requests
"""

import argparse
import csv
import requests
import sys
from datetime import datetime

API_BASE = "https://www.googleapis.com/youtube/v3"


def get_channel_id(handle_or_id: str, api_key: str) -> tuple[str, str]:
    """Resolve a @handle or channel ID to (channel_id, channel_title)."""
    # If it looks like a raw channel ID (starts with UC and ~24 chars), use directly
    if handle_or_id.startswith("UC") and len(handle_or_id) > 20:
        r = requests.get(f"{API_BASE}/channels", params={
            "part": "snippet",
            "id": handle_or_id,
            "key": api_key,
        })
        r.raise_for_status()
        items = r.json().get("items", [])
        if not items:
            sys.exit(f"No channel found for ID: {handle_or_id}")
        return items[0]["id"], items[0]["snippet"]["title"]

    # Otherwise treat as a handle (@name or plain name)
    handle = handle_or_id.lstrip("@")
    r = requests.get(f"{API_BASE}/channels", params={
        "part": "snippet",
        "forHandle": handle,
        "key": api_key,
    })
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        sys.exit(f"No channel found for handle: @{handle}")
    return items[0]["id"], items[0]["snippet"]["title"]


def get_uploads_playlist_id(channel_id: str, api_key: str) -> str:
    """Get the uploads playlist ID for a channel."""
    r = requests.get(f"{API_BASE}/channels", params={
        "part": "contentDetails",
        "id": channel_id,
        "key": api_key,
    })
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        sys.exit("Could not retrieve channel content details.")
    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]


def get_all_video_ids(playlist_id: str, api_key: str) -> list[str]:
    """Page through the uploads playlist to collect all video IDs."""
    video_ids = []
    page_token = None

    while True:
        params = {
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
            "key": api_key,
        }
        if page_token:
            params["pageToken"] = page_token

        r = requests.get(f"{API_BASE}/playlistItems", params=params)
        r.raise_for_status()
        data = r.json()

        for item in data.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return video_ids


def get_video_details(video_ids: list[str], api_key: str) -> list[dict]:
    """Fetch title, view count, and publish date for a list of video IDs (in batches of 50)."""
    videos = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        r = requests.get(f"{API_BASE}/videos", params={
            "part": "snippet,statistics",
            "id": ",".join(batch),
            "key": api_key,
        })
        r.raise_for_status()

        for item in r.json().get("items", []):
            snippet = item["snippet"]
            stats = item.get("statistics", {})
            publish_date = snippet["publishedAt"][:10]  # YYYY-MM-DD
            videos.append({
                "video_id": item["id"],
                "title": snippet["title"],
                "publish_date": publish_date,
                "views": int(stats.get("viewCount", 0)),
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            })

    return videos


def export_csv(videos: list[dict], channel_title: str, output_path: str):
    """Write videos to a CSV file, sorted by publish date descending."""
    videos_sorted = sorted(videos, key=lambda v: v["publish_date"], reverse=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "publish_date", "views", "url", "video_id"])
        writer.writeheader()
        writer.writerows(videos_sorted)

    print(f"\n✅ Exported {len(videos)} videos from '{channel_title}' to: {output_path}")
    print(f"   Date range: {videos_sorted[-1]['publish_date']} → {videos_sorted[0]['publish_date']}")
    print(f"   Total views across all videos: {sum(v['views'] for v in videos):,}")


def main():
    parser = argparse.ArgumentParser(description="Export YouTube channel video data to CSV.")
    parser.add_argument("--channel", required=True, help="Channel handle (e.g. @nateliason) or channel ID")
    parser.add_argument("--api_key", required=True, help="YouTube Data API v3 key")
    parser.add_argument("--output", default=None, help="Output CSV path (default: <channel>_videos.csv)")
    args = parser.parse_args()

    print(f"🔍 Looking up channel: {args.channel}")
    channel_id, channel_title = get_channel_id(args.channel, args.api_key)
    print(f"   Found: {channel_title} ({channel_id})")

    print("📋 Fetching uploads playlist...")
    playlist_id = get_uploads_playlist_id(channel_id, args.api_key)

    print("🎬 Collecting video IDs...")
    video_ids = get_all_video_ids(playlist_id, args.api_key)
    print(f"   Found {len(video_ids)} videos")

    print("📊 Fetching video details...")
    videos = get_video_details(video_ids, args.api_key)

    output_path = args.output or f"{args.channel.lstrip('@')}_videos.csv"
    export_csv(videos, channel_title, output_path)


if __name__ == "__main__":
    main()
