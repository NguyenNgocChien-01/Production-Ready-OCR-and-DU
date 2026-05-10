"""
Base class for all synthetic document generators.
Every generator inherits from DocumentGenerator and implements `generate()`.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from faker import Faker

fake = Faker("en_AU")

WATERMARK_TEXT = "SYNTHETIC DATA"
WATERMARK_COLOR = (220, 30, 30, 30)   # semi-transparent red


@dataclass
class GeneratedDoc:
    image: Image.Image
    label: dict[str, Any]          # ground-truth field values
    doc_type: str


class DocumentGenerator(ABC):
    """Abstract base — subclass one per document type."""

    doc_type: str = "unknown"

    def __init__(self, dpi: int = 150):
        self.dpi = dpi

    # ── public API ──────────────────────────────────────────────

    def generate(self) -> GeneratedDoc:
        """Return a watermarked GeneratedDoc."""
        doc = self._render()
        self._apply_watermark(doc.image)
        return doc

    def generate_batch(self, n: int) -> list[GeneratedDoc]:
        return [self.generate() for _ in range(n)]

    # ── helpers available to subclasses ─────────────────────────

    @staticmethod
    def blank(w: int, h: int, color=(200, 30, 30, 30)) -> Image.Image:
        return Image.new("RGB", (w, h), color)

    @staticmethod
    def draw(img: Image.Image) -> ImageDraw.ImageDraw:
        return ImageDraw.Draw(img)

    @staticmethod
    def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Return a PIL font (falls back gracefully)."""
        candidates = (
            ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
            if bold else
            ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
        )
        for path in candidates:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    @staticmethod
    def _apply_watermark(img: Image.Image) -> None:
        """Stamp a diagonal red watermark across the document."""
        import math
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        try:
            fnt_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            fnt = ImageFont.truetype(fnt_path, size=max(18, img.width // 22))
        except Exception:
            fnt = ImageFont.load_default()

        # repeat text diagonally
        text = WATERMARK_TEXT
        bbox = d.textbbox((0, 0), text, font=fnt)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        step_x = tw + 60
        step_y = th + 40

        for xi in range(2):
            for yi in range(-img.height, img.height * 2, step_y):
                d.text((xi, yi), text, font=fnt, fill=WATERMARK_COLOR)

        # rotate 30°
        rotated = overlay.rotate(30, expand=False)
        if img.mode != "RGBA":
            img_rgba = img.convert("RGBA")
        else:
            img_rgba = img
        combined = Image.alpha_composite(img_rgba, rotated)
        img.paste(combined.convert("RGB"))

    # ── abstract ────────────────────────────────────────────────

    @abstractmethod
    def _render(self) -> GeneratedDoc:
        variant_name = random.choice(["green", "blue"])
        v       = VARIANTS[variant_name]
        members = self._fake_members()
        number  = self._fake_medicare_number()
        expiry  = self._fake_expiry()
        holder  = members[0]   # card holder = người đầu tiên

        img = self.blank(CARD_W, CARD_H, v["bg"])
        d   = self.draw(img)

        self._draw_background_pattern(d, v["pattern"])
        self._draw_logo(d, v["logo_bg"], v["logo_yellow"])
        self._draw_card_number(d, number)
        self._draw_members(d, members)
        self._draw_expiry(d, expiry)
        self._draw_card_border(d, v["border"])

        return GeneratedDoc(
            image=img,
            label={
                "medicare_card_number":      number,
                "medicare_card_first_name":  holder["first_name"],
                "medicare_card_middle_name": holder.get("middle_name", None),
                "medicare_card_last_name":   holder["last_name"],
                "medicare_card_expiry_date": expiry,
                "medicare_card_position":    holder["position"],
                "medicare_card_colour":      variant_name,
                "document_front":  [],   # filled by pipeline khi save
                "document_back":   [],
            },
            doc_type=self.doc_type,
        )
