# Evidence Sources

Use these sources for implementation provenance only. They do not define the
`Hxx` narrative score and are not substitutes for checking a paper's scientific
claims against its source passages.

## ManimAgent

Jiang et al. (2026), "ManimAgent: Self-Evolving Multimodal Agents for Visual Education," arXiv:2606.30296.

Verification: arXiv record checked 2026-07-13; version 2 is dated 2026-07-01.

Relevant idea: scientific-paper sections can be converted into Manim code through a staged agent workflow with reflection and visual review. Use this as architecture inspiration, not as a direct dependency.

URL: https://arxiv.org/abs/2606.30296

## Manim Community

Manim Community documentation describes Manim as an engine for precise programmatic animations and documents MP4 rendering workflows.

Quickstart: https://docs.manim.community/en/stable/tutorials/quickstart.html

Output settings: https://docs.manim.community/en/stable/tutorials/output_and_config.html

## 3Blue1Brown and Manim

The 3Blue1Brown site states that its animations are made with Grant Sanderson's custom open-source Manim library. The community edition is a separate, maintained project forked from that original ecosystem.

3Blue1Brown FAQ: https://www.3blue1brown.com/about/

3Blue1Brown Manim repository: https://github.com/3b1b/manim

Manim Community repository: https://github.com/ManimCommunity/manim

## Practical Interpretation

- Use Manim Community Edition for reproducible research-team work.
- Preserve 3B1B's visual logic: geometry, transformation, sparse text, and intuitive timing.
- Add deterministic export and playback verification because research artifacts must be shareable outside the local machine.
