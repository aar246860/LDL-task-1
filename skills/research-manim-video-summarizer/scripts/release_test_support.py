from __future__ import annotations

import json
import shutil
from hashlib import sha256
from pathlib import Path

from PIL import Image, ImageDraw

from scripts.export_package_content import player_html, qa_notes_text

FIXTURES = Path(__file__).parent / "fixtures"
STATES = ("entry", "midpoint", "settled")


def write_nonblank_image(path: Path, *, offset: int = 0) -> None:
    image = Image.new("RGB", (320, 180), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20 + offset, 30, 170 + offset, 145), fill=(30, 100, 180), outline="black", width=3)
    draw.line((10, 165, 310, 20 + offset), fill=(180, 40, 60), width=6)
    image.save(path)


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _copy_provenance(directory: Path, slug: str) -> dict[str, Path]:
    targets = {
        "scene_source": directory / f"{slug}_scene.py",
        "storyboard": directory / f"{slug}_storyboard.md",
        "source_artifact": directory / f"{slug}_source.md",
        "semantic_audit": directory / f"{slug}_semantic_audit.json",
    }
    sources = {
        "scene_source": FIXTURES / "layout_good_storyboard_mapping.py",
        "storyboard": FIXTURES / "storyboard_good_geometry_first.md",
        "source_artifact": FIXTURES / "storyboard_source_fixture.md",
        "semantic_audit": FIXTURES / "storyboard_semantic_audit_good.json",
    }
    for role, target in targets.items():
        shutil.copy2(sources[role], target)
    return targets


def _write_companions(directory: Path, slug: str, metadata_text: str) -> dict[str, Path]:
    paths = {
        "html": directory / f"{slug}.html",
        "metadata": directory / f"{slug}_metadata.json",
        "qa_notes": directory / f"{slug}_qa.md",
    }
    video_name = f"{slug}.mp4"
    contact_name = f"{slug}_contact_sheet.png"
    paths["html"].write_text(
        player_html(
            title="Atomic research story fixture",
            description="Release validation fixture with ten independently reviewed scenes.",
            mp4_name=video_name,
            contact_sheet_name=contact_name,
        ),
        encoding="utf-8",
    )
    metadata = {
        "title": "Atomic research story fixture",
        "description": "Release validation fixture with ten independently reviewed scenes.",
        "generated_at": "2026-07-14T03:45:35+08:00",
        "artifacts": {
            "mp4": video_name,
            "contact_sheet": contact_name,
            "html": paths["html"].name,
            "qa_notes": paths["qa_notes"].name,
        },
        "ffprobe": metadata_text,
    }
    paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    paths["qa_notes"].write_text(
        qa_notes_text(
            mp4_name=video_name,
            html_name=paths["html"].name,
            contact_sheet_name=contact_name,
            metadata_name=paths["metadata"].name,
            metadata=metadata_text,
        ),
        encoding="utf-8",
    )
    return paths


def make_package(directory: Path, *, slug: str = "summary") -> None:
    video = directory / f"{slug}.mp4"
    contact = directory / f"{slug}_contact_sheet.png"
    shutil.copy2(FIXTURES / "storyboard_reviewed_video.mp4", video)
    shutil.copy2(FIXTURES / "storyboard_reviewed_video_contact_sheet.png", contact)
    provenance = _copy_provenance(directory, slug)
    gold_metadata = json.loads((FIXTURES / "storyboard_reviewed_video_metadata.json").read_text(encoding="utf-8"))
    companions = _write_companions(directory, slug, gold_metadata["ffprobe"])
    manifest = json.loads((FIXTURES / "visual_qa_good.json").read_text(encoding="utf-8"))
    manifest["video_file"] = video.name
    manifest["video_sha256"] = file_digest(video)
    manifest["contact_sheet_file"] = contact.name
    manifest["contact_sheet_sha256"] = file_digest(contact)
    for role, path in {**provenance, **companions}.items():
        manifest[f"{role}_file"] = path.name
        manifest[f"{role}_sha256"] = file_digest(path)
    for record in manifest["scenes"]:
        scene = record["scene"]
        for state in STATES:
            source = FIXTURES / record[f"{state}_frame"]
            target = directory / f"scene{scene}_{state}.png"
            shutil.copy2(source, target)
            record[f"{state}_frame"] = target.name
            record[f"{state}_frame_sha256"] = file_digest(target)
    (directory / f"{slug}_visual_qa.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
