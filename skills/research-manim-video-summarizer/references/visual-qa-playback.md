# Visual QA and Playback Verification

Do not call a research animation complete until it has been driven through its playback surface.

## Required Evidence

1. `ffprobe` metadata:
   - codec
   - profile
   - pixel format
   - width and height
   - duration
   - frame count

2. Browser video evidence:
   - Open the HTML player or raw MP4 through HTTP; require a direct MP4 link and user-initiated play control. Treat a portrait contact sheet as navigation evidence, not a 16:9 poster.
   - Evaluate the `<video>` element.
   - Required values: finite duration, `readyState >= 1`, positive `videoWidth`, positive `videoHeight`, and `error === null`.

3. Contact sheet and scene frames:
   - Treat the exported contact sheet as navigation only; its fixed sampling
     cannot prove scene coverage or collision freedom.
   - Extract entry, midpoint, and settled frames for every scene, regardless of
     scene count.
   - Inspect for text clipping, labels over curves, tiny legends, stale render frames, axes crossing object fills, and halos leaving their physical object.
   - Confirm that every text/data settled state also passed a nonempty runtime
     guard in `check_manim_layout.py`.

4. Transition-frame evidence:
   - Extract the entry, midpoint, and settled frame of every scene transition.
   - Inspect text swaps, camera changes, formula transforms, line-style changes,
     and object handoffs for temporary collisions, reversed time-series paths,
     stale labels, and scrambled glyphs.
   - Reject the render when a collision exists for even a short transition; a
     clean endpoint does not repair unreadable motion.
   - Record every accepted state as the exact value
     `pass: overlap-free and within-frame` in a JSON visual-QA manifest. A
     generic `pass` is invalid, and a manifest is not a substitute for viewing
     the frames.
   - Record the zero-based MP4 frame index and SHA-256 for every extracted
     image. FFmpeg must decode the same RGB pixels at that index.
   - Require decoded pixel content to be globally unique across all scene
     states. Reusing one image in a different scene is a failure.

5. Story coverage:
   - Confirm that every `Bxx` and `Mxx` identifier appears as its own visible
     scene and that no scene silently combines ledger items.
   - Confirm that the opening puzzle, context ladder, mechanism ladder,
     revelation, and final return are visible without relying on narration.
   - Copy each scene's exact storyboard `Visual object` and `Bxx`, `Mxx`, or
     narrative ownership into the manifest. Add a distinct description of what
     is actually visible and sign `visual_semantic_match: pass` only after
     comparing the frame with the storyboard.

6. Web link:
   - Prefer a GitHub Release asset for phone downloads from a private paper repo.
   - Keep the HTML player, contact sheet, metadata JSON, and QA notes in the same release package.
   - Do not rely on a GitHub `blob` URL as the only viewing path or download path.

## Visual-QA Manifest

Use one record per storyboard scene. The checker requires exact scene coverage
and the exact overlap-and-frame decision for entry, midpoint, and settled
states. Each scene declares a contiguous half-open frame range. Entry must lie
at 10-35%, midpoint at 40-65%, and settled at 70-95% of that range; scene ranges
must cover the complete MP4 from frame zero without gaps. The checker reads each
referenced frame, rejects blank or undersized images, rejects absolute or
escaping paths, and requires every state to use a distinct file. Entry,
midpoint, and settled images across the entire video must have distinct pixel
content; renaming or copying an image into another state or scene does not
establish temporal review. Each image also needs its own file hash, zero-based
MP4 frame index, and a distinct substantive content summary. The validator
decodes all selected indices and compares their RGB bytes with the evidence
images.

The top-level provenance fields bind the review to one Manim source file,
storyboard, research source artifact, semantic audit, contact sheet, MP4, HTML
player, metadata JSON, and QA notes. `browser_playback` records the exact finite
duration, positive dimensions, and no-media-error decision.
For publication, all four source-side files must be present in the package and
their manifest file names and hashes must match actual package files.
Calculate SHA-256 after the final render and regenerate the manifest after any
source, storyboard, audit, image, or video change.

```json
{
  "reviewer": "name or review-agent identifier",
  "reviewed_at": "2026-07-13T14:30:00+08:00",
  "review_method": "visual inspection",
  "browser_playback": "pass: finite duration, positive dimensions, no media error",
  "video_file": "paper-summary.mp4",
  "video_sha256": "64 lowercase hexadecimal characters",
  "scene_source_file": "paper-summary_scene.py",
  "scene_source_sha256": "64 lowercase hexadecimal characters",
  "storyboard_file": "paper-summary_storyboard.md",
  "storyboard_sha256": "64 lowercase hexadecimal characters",
  "source_artifact_file": "paper-summary_source.pdf",
  "source_artifact_sha256": "64 lowercase hexadecimal characters",
  "semantic_audit_file": "paper-summary_semantic_audit.json",
  "semantic_audit_sha256": "64 lowercase hexadecimal characters",
  "contact_sheet_file": "paper-summary_contact_sheet.png",
  "contact_sheet_sha256": "64 lowercase hexadecimal characters",
  "html_file": "paper-summary.html",
  "html_sha256": "64 lowercase hexadecimal characters",
  "metadata_file": "paper-summary_metadata.json",
  "metadata_sha256": "64 lowercase hexadecimal characters",
  "qa_notes_file": "paper-summary_qa.md",
  "qa_notes_sha256": "64 lowercase hexadecimal characters",
  "scenes": [
    {
      "scene": 1,
      "scene_start_frame": 0,
      "scene_end_frame": 78,
      "entry": "pass: overlap-free and within-frame",
      "entry_frame": "scene1_entry.png",
      "entry_frame_index": 18,
      "entry_frame_sha256": "64 lowercase hexadecimal characters",
      "entry_content_summary": "Substantive description of the scientific objects visible in the entry state.",
      "midpoint": "pass: overlap-free and within-frame",
      "midpoint_frame": "scene1_midpoint.png",
      "midpoint_frame_index": 42,
      "midpoint_frame_sha256": "64 lowercase hexadecimal characters",
      "midpoint_content_summary": "Substantive description of the changed scientific objects visible at midpoint.",
      "settled": "pass: overlap-free and within-frame",
      "settled_frame": "scene1_settled.png",
      "settled_frame_index": 66,
      "settled_frame_sha256": "64 lowercase hexadecimal characters",
      "settled_content_summary": "Substantive description of the final scientific relation visible in this scene.",
      "storyboard_visual_object": "exact Visual object field copied from Scene 1",
      "storyboard_ownership": "B01",
      "visual_semantic_match": "pass"
    }
  ]
}
```

Pixel checks establish file integrity, temporal identity, and non-reuse. They do
not establish scientific entailment. The named reviewer remains accountable for
the `visual_semantic_match` decision and all three frame-content summaries.

Validate the static code and post-render evidence together:

```bash
uv run scripts/check_manim_layout.py animation/paper_summary_scene.py \
  --contact-sheet output/paper-summary_contact_sheet.png \
  --qa-manifest output/paper-summary_visual_qa.json \
  --storyboard animation/storyboard.md \
  --source-artifact paper.pdf \
  --semantic-audit animation/storyboard_semantic_audit.json
```

## Browser Evaluation Snippet

```js
() => {
  const video = document.querySelector("video");
  return {
    readyState: video?.readyState,
    networkState: video?.networkState,
    duration: Number.isFinite(video?.duration) ? video.duration : String(video?.duration),
    videoWidth: video?.videoWidth,
    videoHeight: video?.videoHeight,
    error: video?.error ? { code: video.error.code, message: video.error.message } : null,
    canPlayMp4: video?.canPlayType('video/mp4; codecs="avc1.42E01F"')
  };
}
```

## Common Failure Modes

- GitHub blob page does not play even when the MP4 exists.
- GitHub raw links are less convenient on phones than release assets.
- MP4 uses a codec profile the browser dislikes.
- `moov` atom is at the end of the file; fix with `-movflags +faststart`.
- CJK labels are clipped because text boxes were sized for English.
- Labels look syntactically positioned with `next_to` but still collide with
  aquifer blocks, axes, curves, or point clouds in the rendered frame.
- Support-volume circles are centered on the right idea but visually extend
  outside the aquifer or specimen they are supposed to describe.
- K/Y labels sit on top of density curves, pull lines, arrows, or axis ticks.
- Data-reveal animations draw too quickly for the viewer to see which geometry
  changed; slow them down and use smooth easing before final approval.
- Preview frames were extracted during transitions, making contact sheets misleading.
