# Research Video QA Notes

## Exported Artifacts

- MP4: `storyboard_reviewed_video.mp4`
- HTML player: `storyboard_reviewed_video.html`
- Contact sheet: `storyboard_reviewed_video_contact_sheet.png`
- Metadata: `storyboard_reviewed_video_metadata.json`

## ffprobe Metadata

```text
codec_name=h264
profile=Constrained Baseline
width=854
height=480
pix_fmt=yuv420p
level=31
duration=26.000000
nb_frames=780
format_name=mov,mp4,m4a,3gp,3g2,mj2
duration=26.000000
size=261113
```

## Required Manual Review

- Open the HTML player in a browser.
- Confirm the video has finite duration, positive width and height, and no media error.
- Treat the contact sheet as navigation only; review per-scene entry, midpoint, and settled frames separately.
- Mark a scene state pass only when visual inspection confirms it is overlap-free and within-frame; a generic pass label is invalid.
- Extract three nonblank frames per scene: entry, midpoint, and settled. Record each zero-based MP4 frame index, relative image path, and image SHA-256; all indices and decoded RGB images must be globally unique.
- Decode the declared MP4 indices with FFmpeg and require exact RGB-pixel equality with the reviewed images. Renamed, repeated, or unrelated images do not count as evidence.
- Record a named reviewer, timezone-aware ISO reviewed_at time, review_method set to visual inspection, pass decisions, and a substantive visual-content summary for every scene state in the visual-QA manifest.
- Bind the visual-QA manifest to the Manim source, storyboard, research source, semantic audit, contact sheet, and MP4 with verified file names and SHA-256 values; regenerate it after any artifact changes.
- Publish only after the user explicitly authorizes a live GitHub Release.
