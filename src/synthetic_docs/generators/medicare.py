"""
Medicare Card Generator
Layout ref: green card, 757x444px at screen res.
"""
from __future__ import annotations
import random
import uuid
from PIL import Image, ImageDraw

from .base import DocumentGenerator, GeneratedDoc, fake


# ── palette ────────────────────────────────────────────────────
BG_GREEN      = (210, 230, 200)
CARD_GREEN    = (180, 215, 175)
TEXT_DARK     = (20,  20,  20)
LOGO_GREEN    = (0,   130,  60)
LOGO_YELLOW   = (255, 200,   0)
PATTERN_GREEN = (160, 200, 155)

CARD_W, CARD_H = 760, 445


class MedicareGenerator(DocumentGenerator):
    doc_type = "medicare_card"

    # ── fake data ───────────────────────────────────────────────

    def _fake_medicare_number(self) -> str:
        """10 digits continuous"""
        d = [str(random.randint(0, 9)) for _ in range(10)]
        return "".join(d)

    def _fake_members(self) -> list[dict]:
        n = random.randint(1, 4)
        last_name = fake.last_name().upper()
        return [
            {
                "position":   str(i + 1),
                "first_name": fake.first_name().upper(),
                "last_name":  last_name,
            }
            for i in range(n)
        ]
        
    def _fake_expiry(self) -> str:
        m = random.randint(1, 12)
        y = random.randint(2025, 2030)
        return f"{m:02d}/{y}"

    # ── render ──────────────────────────────────────────────────

    def _render(self) -> GeneratedDoc:
        img   = self.blank(CARD_W, CARD_H, CARD_GREEN)
        d     = self.draw(img)

        members = self._fake_members()
        number  = self._fake_medicare_number()
        expiry  = self._fake_expiry()
        
        # Chọn ngẫu nhiên 1 thành viên trên thẻ làm mục tiêu trích xuất
        target_member = random.choice(members)

        self._draw_background_pattern(d)
        self._draw_logo(d, img)
        
        # Thêm khoảng trắng khi vẽ để giống thẻ thật, nhưng giữ chuỗi gốc không khoảng trắng cho nhãn
        display_number = f"{number[:4]} {number[4:9]} {number[9]}"
        self._draw_card_number(d, display_number)
        
        self._draw_members(d, members)
        self._draw_expiry(d, expiry)
        self._draw_card_border(d)
        
        # Giả lập đường dẫn lưu trữ
        front_image_path = f"s3://volta-ai-training/synthetic/medicare/{uuid.uuid4()}_front.jpg"

        return GeneratedDoc(
            image=img,
            label=dict(
                medicare_card_number=number,
                medicare_card_first_name=target_member["first_name"],
                medicare_card_middle_name=None,
                medicare_card_last_name=target_member["last_name"],
                medicare_card_expiry_date=expiry,
                medicare_card_position=target_member["position"],
                medicare_card_colour="green",
                document_front=[front_image_path],
                document_back=[]
            ),
            doc_type=self.doc_type,
        )

    # ── drawing helpers ─────────────────────────────────────────

    def _draw_background_pattern(self, d: ImageDraw.ImageDraw) -> None:
        """Tiled 'medicare' text watermark (like the real card)."""
        fnt = self.font(9)
        for y in range(0, CARD_H, 16):
            for x in range(0, CARD_W, 68):
                offset = 34 if (y // 16) % 2 else 0
                d.text((x + offset, y), "medicare", fill=PATTERN_GREEN, font=fnt)

    def _draw_logo(self, d: ImageDraw.ImageDraw, img: Image.Image) -> None:
        """Green 'medicare' logo pill in top-right."""
        rx, ry, rw, rh = CARD_W - 185, 18, 165, 48
        d.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=10, fill=LOGO_GREEN)
        fnt = self.font(26, bold=True)
        d.text((rx + 10, ry + 6), "m", fill=LOGO_YELLOW, font=fnt)
        fnt2 = self.font(22, bold=True)
        d.text((rx + 33, ry + 10), "edicare", fill=(255, 255, 255), font=fnt2)

    def _draw_card_number(self, d: ImageDraw.ImageDraw, number: str) -> None:
        fnt = self.font(42, bold=True)
        d.text((55, 100), number, fill=TEXT_DARK, font=fnt)

    def _draw_members(self, d: ImageDraw.ImageDraw, members: list[dict]) -> None:
        fnt = self.font(22, bold=True)
        y = 175
        for m in members:
            # Chữ "A" giả lập tên đệm ngẫu nhiên như trong mã gốc
            line = f"{m['position']}  {m['first_name']}  A  {m['last_name']}"
            d.text((55, y), line, fill=TEXT_DARK, font=fnt)
            y += 38
            
    def _draw_expiry(self, d: ImageDraw.ImageDraw, expiry: str) -> None:
        fnt_label = self.font(18)
        fnt_val   = self.font(20, bold=True)
        d.text((55, CARD_H - 60), "VALID TO", fill=TEXT_DARK, font=fnt_label)
        d.text((160, CARD_H - 61), expiry, fill=TEXT_DARK, font=fnt_val)

    def _draw_card_border(self, d: ImageDraw.ImageDraw) -> None:
        d.rounded_rectangle(
            [4, 4, CARD_W - 4, CARD_H - 4],
            radius=22,
            outline=(120, 170, 120),
            width=4,
        )