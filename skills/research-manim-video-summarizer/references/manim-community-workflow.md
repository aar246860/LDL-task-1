# Manim Community Workflow

Use Manim Community Edition for stable research video output. Do not target the 3Blue1Brown custom ManimGL API unless the user explicitly requests that fork.

## Recommended Project Shape

```text
animation/
├── storyboard.md
├── storyboard.py
├── mobjects.py
├── paper_summary_scene.py
└── output/
```

Use one main `Scene` class when continuous morphing matters. Use one directly rendered helper method per storyboard scene. Begin every helper with its two-digit storyboard number, followed by its `Bxx`, `Mxx`, or result role, such as `scene_02_b02_prior_limit`, `scene_07_m04_residual_field`, and `scene_10_return_to_aquifer`. Call all numbered helpers exactly once and in order from `construct`; the post-render checker compares this sequence with the storyboard and QA manifest. Do not combine ledger items inside one helper.

## Render Commands

Quick preview:

```bash
uv run --python 3.11 --with manim manim -ql --media_dir animation/media animation/paper_summary_scene.py PaperSummaryScene
```

Review render:

```bash
uv run --python 3.11 --with manim manim -qm --media_dir animation/media animation/paper_summary_scene.py PaperSummaryScene
```

High-resolution render:

```bash
uv run --python 3.11 --with manim manim -qh --media_dir animation/media animation/paper_summary_scene.py PaperSummaryScene
```

## Coding Rules

- Use `Text` with a CJK-capable font when Chinese text is present.
- Use `self.wait()` after important visual transformations.
- Prefer helper functions for axes, distributions, curves, and labels.
- Keep formulas short; use `MathTex` only after the geometry has been introduced.
- Export frame previews after every meaningful revision.
- Call `assert_scene_layout(scene=self, pending_items=[...], labels=[...], blockers=[...], frame_items=[...])` inside every scene helper that combines text with data geometry and before every `add` or `play` that establishes a settled state. `frame_items` must cover every current `self.mobjects` family plus every object in `pending_items`; labels and blockers must be nonempty. A guard in `construct`, another helper, or an earlier state does not count.
- Labels and blockers must also be members of the current scene or `pending_items` and of `frame_items`. An off-screen or detached object cannot satisfy the role lists.
- For pure geometry, call `assert_within_frame([...], scene=self, pending_items=[...])` before each settled state. This coverage check prevents a newly introduced or previously visible object from escaping review.
- When scientific geometry must overlap, list every allowed top-level pair in the storyboard and pass the same object pairs through `intentional_overlaps`. The guard rejects all other bounding-box intersections; never use a global overlap bypass.
- Do not use `.animate` in code submitted to the strict static checker. Construct and position a target copy, run the appropriate layout guard on that target and all current objects, then use an explicit same-object-state transform. Use `FadeOut` and `FadeIn` for unrelated labels.

## Transition And Pacing Rules

- Do not raw-transform unrelated prose. CJK labels, titles, scene captions, and long prose should switch with `FadeOut` followed by `FadeIn`. Use `TransformMatchingShapes` only when the visible characters or symbols intentionally correspond.
- Separate geometry morphs from text changes. A shape can morph while its old label fades out and the new label fades in; avoid bundling both into one `Transform`.
- Preserve spatial orientation. Cross-section to plan view, map to section, or 2D to 3D changes need either a camera bridge that explains the viewpoint change or a full fade/clear transition. Never morph columns, aquifer blocks, or section arrows into plan-view building footprints or contour blobs.
- Use visual hierarchy. Before highlighting anisotropy, heat flux, plume propagation, or uncertainty intervals, dim the background geometry and keep the active path, band, or interval at highest contrast.
- Pace concept boundaries. After formulas, view changes, uncertainty intervals, or final result summaries, use a readable pause, usually 1.2-2.0 seconds for a 720p review render, before introducing the next idea.
- Review frames near text swaps and view changes, not only stable ending frames. These are the failure points where glyph scrambling, object collisions, or spatial disorientation usually appear.
- For every transition, inspect entry, midpoint, and settled frames and record them in the visual-QA manifest. A clean settled frame does not excuse a collision during motion.
- Record a zero-based MP4 frame index and SHA-256 for every reviewed image. The indices and decoded RGB images must be globally unique, and FFmpeg must reproduce every reviewed image exactly from the declared MP4 frame. A contact sheet or three renamed copies is not frame evidence.
- For every scene, record its contiguous frame range, the exact storyboard visual object, its `Bxx`, `Mxx`, or result owner, and separate substantive entry, midpoint, and settled summaries. A named reviewer must confirm the visual claim; pixel equality alone cannot establish scientific meaning.

## Web Export

Manim output is not always ideal for browser playback. Re-encode final MP4:

```bash
ffmpeg -y -i input.mp4 -c:v libx264 -profile:v baseline -level 3.1 -pix_fmt yuv420p -preset medium -crf 23 -movflags +faststart -an output.mp4
```

Then verify in a real browser, not only with `ffprobe`. The release package must also contain the exact scene source, storyboard, research source, and signed semantic audit named and hashed by the visual-QA manifest.
