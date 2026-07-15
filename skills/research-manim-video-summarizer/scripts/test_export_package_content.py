from __future__ import annotations

import pytest
import typer

from scripts.export_manim_video import validated_slug
from scripts.export_package_content import ExportContentError, player_html, qa_notes_text


def test_player_html_escapes_user_text_and_replaces_markers() -> None:
    html = player_html(
        title='<script>alert("x")</script>',
        description="A < B & C",
        mp4_name='video".mp4',
        contact_sheet_name="sheet.png",
    )

    assert "&lt;script&gt;alert" in html
    assert "&lt;script&gt;" in html
    assert "A &lt; B &amp; C" in html
    assert "video&quot;.mp4" in html
    assert "{{" not in html


def test_template_markers_in_user_text_are_not_reprocessed() -> None:
    html = player_html(
        title="Keep {{MP4}} literal",
        description="Marker test",
        mp4_name="video.mp4",
        contact_sheet_name="sheet.png",
    )

    assert "Keep {{MP4}} literal" in html


@pytest.mark.parametrize("asset", ("../video.mp4", "https://example.com/video.mp4", r"dir\video.mp4"))
def test_player_rejects_nonlocal_asset_names(asset: str) -> None:
    with pytest.raises(ExportContentError):
        player_html(
            title="Title",
            description="Description",
            mp4_name=asset,
            contact_sheet_name="sheet.png",
        )


@pytest.mark.parametrize("slug", ("../escape", "..", "dir/name", r"dir\name", "https:video"))
def test_export_slug_cannot_escape_output_directory(slug: str) -> None:
    with pytest.raises(typer.BadParameter):
        validated_slug(slug)


def test_export_slug_accepts_safe_file_token() -> None:
    assert validated_slug("paper-summary_v2.1") == "paper-summary_v2.1"


def test_qa_notes_require_three_state_scene_review() -> None:
    notes = qa_notes_text(
        mp4_name="video.mp4",
        html_name="video.html",
        contact_sheet_name="sheet.png",
        metadata_name="metadata.json",
        metadata="width=1920\nheight=1080",
    )

    assert "entry, midpoint, and settled" in notes
    assert "visual-QA manifest" in notes
    assert "research source, semantic audit" in notes
    assert "explicitly authorizes" in notes
