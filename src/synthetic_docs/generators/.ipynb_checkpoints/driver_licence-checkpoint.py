"""
Driver Licence Generator — Victoria, Australia (matching real layout)

Layout (landscape card):
  FRONT:
    - blue header bar: "DRIVER LICENCE / VICTORIA AUSTRALIA"
    - green guilloche background pattern
    - Name, Address (top-left)
    - Grey stripe across middle: LICENCE EXPIRY | DATE OF BIRTH
    - LICENCE TYPE | CONDITIONS (oval outline)
    - LICENCE NO. (top-right area)
    - Photo placeholder (right)
    - VicRoads logo (bottom-right)
    - Watermark number across photo (like real card)

  BACK:
    - CONDITIONS table (letters + descriptions)
    - Reflected expiry/DOB (upside-down ghost)
    - Barcode bottom-right
    - VicRoads text
"""
from __future__ import annotations
import random
import string
from datetime import date
from PIL import Image, ImageDraw
from faker import Faker

from .base import DocumentGenerator, GeneratedDoc, fake

# ── canvas ────────────────────────────────────────────────────
CW, CH = 860, 540     # front card (landscape)

# ── palette ───────────────────────────────────────────────────
C_BG          = (218, 232, 208)   # light green card bg
C_HEADER      = (22,  52, 128)    # blue header
C_HEADER_TXT  = (255, 255, 255)
C_STRIPE      = (185, 195, 185)   # grey mid stripe
C_DARK        = (12,  12,  12)
C_GREY        = (85,  85,  85)
C_LOGO_GREEN  = (0,   148,  60)
C_LOGO_BLUE   = (0,   80,  160)
C_COND_RED    = (185,  40,  40)   # conditions oval
C_PHOTO_BG    = (200, 205, 195)
C_GUILLOCHE   = (200, 220, 192)   # faint pattern

AU_STATES = ["VIC", "NSW", "QLD", "SA", "WA", "TAS", "ACT", "NT"]

CONDITIONS_MAP = {
    "A": "Automatic Transmission",
    "B": "Synchromesh Transmission — Heavy Vehicle",
    "C": "Corrective Lenses Required",
    "E": "LAMS & No Pillion Passenger Restriction",
    "S": "Corrective lenses to be worn while driving",
    "V": "Automatic",
    "X": "Condition Line Number Six",
    "Y": "Condition Line Number Seven",
    "Z": "Condition Line Number Eight",
}


class DriverLicenceGenerator(DocumentGenerator):
    doc_type = "driver_licence"

    # ── fake helpers ─────────────────────────────────────────

    def _licence_no(self) -> str:
        return "".join(random.choices(string.digits, k=9))

    def _dob(self) -> date:
        return fake.date_of_birth(minimum_age=18, maximum_age=80)

    def _expiry(self) -> date:
        return fake.date_between(start_date="+1y", end_date="+8y")

    def _address(self) -> tuple[str, str]:
        num    = random.randint(1, 200)
        street = fake.street_name().upper()
        flat   = f"FLAT {random.randint(1,20)}  " if random.random() < 0.4 else ""
        suburb = fake.city().upper()
        post   = str(random.randint(3000, 3999))
        return (
            f"{flat}{num} {street}",
            f"{suburb} VIC {post}",
        )

    def _conditions(self) -> str:
        pool = list(CONDITIONS_MAP.keys())
        k    = random.randint(1, 5)
        return "".join(sorted(random.sample(pool, k)))

    # ── render ────────────────────────────────────────────────

    def _render(self) -> GeneratedDoc:
        first  = fake.first_name().upper()
        mid    = random.choice([fake.first_name()[0].upper() + " ", ""])
        last   = fake.last_name().upper()
        full   = f"{first} {mid}{last}".strip()
        addr   = self._address()
        lic_no = self._licence_no()
        dob    = self._dob()
        expiry = self._expiry()
        conds  = self._conditions()

        front = self.blank(CW, CH, C_BG)
        self._draw_front(self.draw(front), full, addr, lic_no, dob, expiry, conds)

        back = self.blank(CW, CH, (245, 245, 242))
        self._draw_back(self.draw(back), lic_no, dob, expiry, conds)

        return GeneratedDoc(
            image=front,
            # image_back=back,
            label={
                "driver_licence_first_name":    first,
                "driver_licence_middle_name":   mid.strip() or None,
                "driver_licence_last_name":     last,
                "driver_licence_number":        lic_no,
                "driver_licence_date_of_birth": dob.strftime("%Y-%m-%d"),
                "driver_licence_expiry_date":   expiry.strftime("%Y-%m-%d"),
                "driver_licence_state":         "VIC",
                "driver_licence_address":       " ".join(addr),
                "document_front":               [],
                "document_back":                [],
            },
            doc_type=self.doc_type,
        )

    # ── FRONT ─────────────────────────────────────────────────

    def _draw_front(self, d, full, addr, lic_no, dob, expiry, conds):
        self._guilloche(d)
        self._header(d)
        self._name_address(d, full, addr)
        self._licence_no_block(d, lic_no)
        self._mid_stripe(d, expiry, dob)
        self._type_conditions(d, conds)
        self._photo_placeholder(d, lic_no)
        self._vicroads_logo(d)
        self._front_border(d)

    def _guilloche(self, d):
        """Faint wavy lines across card bg."""
        import math
        for i in range(0, CH, 10):
            pts = [(x, i + int(4 * math.sin(x * 0.05 + i * 0.1)))
                   for x in range(0, CW, 4)]
            d.line(pts, fill=C_GUILLOCHE, width=1)

    def _header(self, d):
        d.rectangle([0, 0, CW, 52], fill=C_HEADER)
        d.text((20, 8),  "DRIVER LICENCE",
               fill=C_HEADER_TXT, font=self.font(18, bold=True))
        d.text((20, 30), "VICTORIA  AUSTRALIA",
               fill=(180, 205, 255), font=self.font(13, bold=True))

    def _name_address(self, d, full, addr):
        d.text((22, 62), full,    fill=C_DARK, font=self.font(17, bold=True))
        d.text((22, 88), addr[0], fill=C_DARK, font=self.font(12))
        d.text((22, 106),addr[1], fill=C_DARK, font=self.font(12))

    def _licence_no_block(self, d, lic_no):
        d.text((410, 62), "LICENCE NO.",
               fill=C_GREY, font=self.font(11))
        d.text((410, 78), lic_no,
               fill=C_DARK, font=self.font(16, bold=True))

    def _mid_stripe(self, d, expiry, dob):
        sy = 130
        d.rectangle([0, sy, CW-220, sy+68], fill=C_STRIPE)
        fl  = self.font(11)
        fv  = self.font(15, bold=True)

        d.text((22,  sy+4),  "LICENCE EXPIRY", fill=C_GREY, font=fl)
        d.text((200, sy+4),  "DATE OF BIRTH",  fill=C_GREY, font=fl)
        d.text((22,  sy+22), expiry.strftime("%d-%m-%Y"), fill=C_DARK, font=fv)
        d.text((200, sy+22), dob.strftime("%d-%m-%Y"),    fill=C_DARK, font=fv)

    def _type_conditions(self, d, conds):
        fy = 218
        fl = self.font(11)
        fv = self.font(14, bold=True)

        d.text((22,  fy),    "LICENCE TYPE", fill=C_GREY, font=fl)
        d.text((180, fy),    "CONDITIONS",   fill=C_GREY, font=fl)
        d.text((22,  fy+16), "CAR",          fill=C_DARK, font=fv)

        # conditions in oval
        cx, cy = 185, fy + 24
        tw = len(conds) * 10 + 20
        d.ellipse([cx-4, cy-16, cx+tw, cy+12],
                  outline=C_COND_RED, width=2)
        d.text((cx+4, cy-13), conds, fill=C_DARK, font=fv)

        # signature line
        d.line([(22, CH-55), (200, CH-55)], fill=C_GREY, width=1)
        d.text((22, CH-50), "Signature", fill=C_GREY, font=self.font(10))

    def _photo_placeholder(self, d, lic_no):
        px, py = CW-205, 58
        pw, ph = 188, 248
        d.rectangle([px, py, px+pw, py+ph],
                    fill=C_PHOTO_BG, outline=(160,165,158), width=1)
        d.text((px+52, py+ph//2-8), "PHOTO",
               fill=(128,130,125), font=self.font(14))

        # watermark number across photo (like real card)
        fnt_wm = self.font(22, bold=True)
        d.text((px+8, py+ph//2+18), lic_no[:5],
               fill=(160,165,158), font=fnt_wm)

    def _vicroads_logo(self, d):
        # green chevron "N" + vicroads text
        d.text((CW-200, CH-38), "N vicroads",
               fill=C_LOGO_GREEN, font=self.font(16, bold=True))

    def _front_border(self, d):
        d.rounded_rectangle([3, 3, CW-3, CH-3],
                             radius=20, outline=(90,130,90), width=3)

    # ── BACK ──────────────────────────────────────────────────

    def _draw_back(self, d, lic_no, dob, expiry, conds):
        # "CARRY LICENCE WHEN DRIVING" top right
        d.text((CW-285, 14), "CARRY LICENCE WHEN DRIVING",
               fill=(40,40,40), font=self.font(11))

        # CONDITIONS table left
        d.text((22, 14), "CONDITIONS",
               fill=(40,40,40), font=self.font(12, bold=True))
        y = 36
        fl = self.font(11)
        for letter in sorted(conds):
            desc = CONDITIONS_MAP.get(letter, "Condition")
            d.text((22,  y), letter, fill=(40,40,40), font=self.font(12, bold=True))
            d.text((46,  y), desc,   fill=(40,40,40), font=fl)
            y += 18

        # reflected dates (ghost upside-down — simplified)
        d.text((22, CH-90), "LICENCE EXPIRY",
               fill=(160,160,160), font=self.font(10))
        d.text((22, CH-75), expiry.strftime("%d-%m-%Y"),
               fill=(160,160,160), font=self.font(12))
        d.text((200, CH-90), "DATE OF BIRTH",
               fill=(160,160,160), font=self.font(10))
        d.text((200, CH-75), dob.strftime("%d-%m-%Y"),
               fill=(160,160,160), font=self.font(12))

        # barcode simulation (right)
        bx = CW - 140
        for i in range(0, 90, random.choice([2, 3, 4])):
            w = random.randint(1, 3)
            d.rectangle([bx+i, CH-120, bx+i+w-1, CH-50], fill=(20,20,20))

        d.text((bx, CH-40), "D" + lic_no[:7],
               fill=(40,40,40), font=self.font(10))

        # VicRoads text bottom
        d.text((22, CH-30), "VicRoads must be notified of your CHANGE OF ADDRESS",
               fill=(60,60,60), font=self.font(9))
        d.text((22, CH-16), "by visiting www.vicroads.vic.gov.au or telephoning 131171",
               fill=(60,60,60), font=self.font(9))

        # border
        d.rounded_rectangle([3, 3, CW-3, CH-3],
                             radius=20, outline=(160,160,155), width=2)