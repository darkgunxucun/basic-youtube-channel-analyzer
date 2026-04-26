# Basic YouTube Channel Analyzer

A lightweight Python script that fetches all videos from any public YouTube channel and exports the data to a CSV file for further analysis.

## What it does

- Looks up any YouTube channel by handle (e.g. `@nateliason`) or channel ID
- Retrieves all uploaded videos via the YouTube Data API v3
- Exports a CSV with: video title, publish date, view count, video URL, and video ID
- Results are sorted newest-first

## Requirements

- Python 3.10+
- A [YouTube Data API v3 key](https://console.cloud.google.com/)

## Installation

1. Clone the repo:
```bash
   git clone https://github.com/darkgunxucun/basic-youtube-channel-analyzer.git
   cd basic-youtube-channel-analyzer
```

2. Install the dependency:
```bash
   pip3 install requests
```

## Usage

```bash
python3 youtube_channel_analyzer.py --channel @handle --api_key YOUR_API_KEY
```

**Examples:**
```bash
python3 youtube_channel_analyzer.py --channel @nateliason --api_key YOUR_API_KEY
python3 youtube_channel_analyzer.py --channel @CombiningMinds --api_key YOUR_API_KEY
```

By default, the CSV is saved as `<handle>_videos.csv` in the current directory. Use `--output` to specify a custom path:
```bash
python3 youtube_channel_analyzer.py --channel @nateliason --api_key YOUR_API_KEY --output ~/Documents/nate.csv
```

## Output

| Column | Description |
|---|---|
| `title` | Video title |
| `publish_date` | Date published (YYYY-MM-DD) |
| `views` | Total view count |
| `url` | Direct link to the video |
| `video_id` | YouTube video ID |

## Getting a YouTube Data API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3** under APIs & Services → Library
4. Go to APIs & Services → Credentials → Create Credentials → API Key
5. Restrict the key to YouTube Data API v3 only (recommended)

## License

MIT
