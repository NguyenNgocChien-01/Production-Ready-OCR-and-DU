
"""
Passport Generator — Australian Passport (closely matching real layout)

Layout (portrait):
  TOP HALF  : blue-grey bg, Parliament House silhouette, OBSERVATIONS text,
              wave security lines, dot matrix, small photo top-right
  BOTTOM HALF: white data page
    - header: TITRE DE VOYAGE | gold AUS box | AUSTRALIA | DOCUMENT No.
    - left  : large photo placeholder
    - right : Type, Name, Nationality, DOB, Sex, POB, Issue, Expiry, Authority
    - teal security emblem
    - MRZ 2 lines at bottom
"""
from __future__ import annotations
import math
import random
import string
from datetime import date
from PIL import Image, ImageDraw
from faker import Faker

from .base import DocumentGenerator, GeneratedDoc, fake

W, H    = 900, 1280
TOP_H   = 560
DATA_Y  = TOP_H

C_SKY      = (172, 195, 218)
C_SKY_DK   = (140, 165, 192)
C_SKY_LN   = (155, 180, 205)
C_WHITE    = (250, 250, 248)
C_BLACK    = (15,  15,  15)
C_LABEL    = (120, 120, 120)
C_BLUE_HDR = (28,  62, 135)
C_GOLD     = (185, 145,  25)
C_TEAL     = (85,  155, 148)
C_MRZ_BG   = (232, 236, 242)
C_DOT      = (148, 172, 198)
C_BORDER   = (95,  118, 145)

AU_CITIES = [
    "SYDNEY", "MELBOURNE", "BRISBANE", "PERTH", "ADELAIDE",
    "CANBERRA", "HOBART", "DARWIN", "GOLD COAST", "NEWCASTLE",
    "WOLLONGONG", "GEELONG", "TOWNSVILLE", "CAIRNS",
]


class PassportGenerator(DocumentGenerator):
    doc_type = "passport"

    def _passport_no(self) -> str:
        return (
            "".join(random.choices(string.ascii_uppercase, k=2))
            + "".join(random.choices(string.digits, k=7))
        )

    def _dob(self) -> date:
        return fake.date_of_birth(minimum_age=18, maximum_age=75)

    def _issue(self) -> date:
        return fake.date_between(start_date="-9y", end_date="-1y")

    def _expiry(self, issue: date) -> date:
        return issue.replace(year=issue.year + 10)

    def _mrz(self, last, first, mid, pno, dob, exp, sex):
        def pad(s, n):
            return (s.replace(" ", "<") + "<" * n)[:n]
        name = last + "<<" + first + ("<" + mid if mid else "")
        l1 = "P<AUS" + pad(name, 39)
        l2 = (pad(pno, 9) + "0AUS"
              + dob.strftime("%y%m%d") + sex
              + exp.strftime("%y%m%d") + "0" + "<" * 14 + "0")
        return l1[:44], l2[:44]

    def _render(self) -> GeneratedDoc:
        first  = fake.first_name().upper()
        mid    = random.choice([fake.first_name().upper(), None, None])
        last   = fake.last_name().upper()
        sex    = random.choice(["M", "F"])
        dob    = self._dob()
        issue  = self._issue()
        expiry = self._expiry(issue)
        pno    = self._passport_no()
        pob    = random.choice(AU_CITIES)
        mrz1, mrz2 = self._mrz(last, first, mid, pno, dob, expiry, sex)

        img = self.blank(W, H, C_WHITE)
        d   = self.draw(img)

        self._top(d)
        self._data(d, first, mid, last, pno, sex, dob, issue, expiry, pob, mrz1, mrz2)
        d.rectangle([0, 0, W-1, H-1], outline=C_BORDER, width=5)
        d.line([(0, TOP_H), (W, TOP_H)], fill=C_BORDER, width=2)

        return GeneratedDoc(
            image=img,
            # image_back=None,
            label={
                "passport_first_name":     first,
                "passport_middle_name":    mid,
                "passport_last_name":      last,
                "passport_number":         pno,
                "passport_date_of_birth":  dob.strftime("%Y-%m-%d"),
                "passport_expiry_date":    expiry.strftime("%Y-%m-%d"),
                "passport_nationality":    "AUSTRALIAN",
                "passport_gender":         sex,
                "passport_place_of_birth": pob,
                "passport_mrz_line1":      mrz1,
                "passport_mrz_line2":      mrz2,
                "document_front":          [],
                "document_back":           [],
            },
            doc_type=self.doc_type,
        )

    # ── TOP ───────────────────────────────────────────────────

    def _top(self, d):
        d.rectangle([0, 0, W, TOP_H], fill=C_SKY)

        # wave lines
        for row in range(0, TOP_H, 14):
            pts = [(x, row + int(5 * math.sin((x + row*4) * 0.035)))
                   for x in range(0, W, 3)]
            d.line(pts, fill=C_SKY_LN, width=1)

        # Parliament House
        # by = TOP_H - 40
        # d.rectangle([100, by+10, 800, by+55], fill=C_SKY_DK)   # forecourt
        # d.rectangle([170, by-35, 730, by+10], fill=C_SKY_DK)   # main body
        # d.rectangle([435, by-140, 455, by-35], fill=C_SKY_DK)  # mast
        # d.rectangle([455, by-132, 498, by-115], fill=C_SKY_DK) # flag
        # d.polygon([(100,by+10),(170,by-35),(170,by+10)], fill=C_SKY_DK)
        # d.polygon([(730,by-35),(800,by+10),(730,by+10)], fill=C_SKY_DK)
        # d.rectangle([100, by+55, 800, by+75], fill=(158,182,205)) # reflection

        # dot matrix left
        for row in range(10):
            for col in range(8):
                cx = 28 + col*9
                cy = 285 + row*9
                d.ellipse([cx, cy, cx+3, cy+3], fill=C_DOT)

        # OBSERVATIONS text
        d.text((52, 34), "OBSERVATIONS",
               fill=C_BLACK, font=self.font(18, bold=True))
        lines = [
            "This document is valid for all countries unless",
            "otherwise endorsed (subject to the visa, permit",
            "or other entry requirements of each country).",
            "À moins d'indication contraire, ce document",
            "est valable pour tous pays (sous réserve des",
            "conditions de délivrance de visa, de permis,",
            "ou autres conditions d'entrée de chaque pays).",
        ]
        y = 68
        for line in lines:
            d.text((52, y), line, fill=C_BLACK, font=self.font(11))
            y += 17

        # small photo top-right
        px, py, pw, ph = W-165, 28, 138, 175
        d.rectangle([px, py, px+pw, py+ph],
                    fill=(205,212,220), outline=(155,168,185), width=1)
        d.text((px+32, py+ph//2-7), "PHOTO",
               fill=(130,140,152), font=self.font(13))

    # ── DATA ──────────────────────────────────────────────────

    def _data(self, d, first, mid, last, pno, sex,
              dob, issue, expiry, pob, mrz1, mrz2):
        Y = DATA_Y

        # subtle bg dots
        for row in range(0, H-Y, 12):
            for col in range(0, W, 12):
                d.ellipse([col+5, Y+row+5, col+7, Y+row+7],
                          fill=(218,222,218))

        # header
        d.text((52, Y+16), "TITRE DE VOYAGE",
               fill=C_BLUE_HDR, font=self.font(13, bold=True))
        d.rounded_rectangle([205, Y+12, 268, Y+40], radius=4, fill=C_GOLD)
        d.text((214, Y+17), "AUS",
               fill=(255,255,255), font=self.font(14, bold=True))
        d.text((282, Y+12), "AUSTRALIA",
               fill=C_BLACK, font=self.font(14, bold=True))
        d.text((W-230, Y+12), "DOCUMENT No.",
               fill=C_LABEL, font=self.font(10))
        d.text((W-230, Y+26), pno,
               fill=C_BLACK, font=self.font(15, bold=True))
        d.line([(52, Y+52), (W-52, Y+52)], fill=(195,200,195), width=1)

        # large photo
        phx, phy, phw, phh = 52, Y+62, 195, 248
        d.rectangle([phx, phy, phx+phw, phy+phh],
                    fill=(210,212,210), outline=(165,168,165), width=1)
        d.text((phx+50, phy+phh//2-7), "PHOTO",
               fill=(135,135,135), font=self.font(14))

        # teal security emblem right
        ex, ey = W-110, Y+185
        for r in [50, 40, 30, 20, 11]:
            d.ellipse([ex-r, ey-r, ex+r, ey+r], outline=C_TEAL, width=1)
        d.line([(ex-58, ey), (ex+58, ey)], fill=C_TEAL, width=1)
        d.line([(ex, ey-58), (ex, ey+58)], fill=C_TEAL, width=1)
        d.line([(ex-40, ey-40), (ex+40, ey+40)], fill=C_TEAL, width=1)
        d.line([(ex+40, ey-40), (ex-40, ey+40)], fill=C_TEAL, width=1)

        # fields
        def lbl(text, x, y):
            d.text((x, y), text, fill=C_LABEL, font=self.font(10))

        def val(text, x, y, size=15):
            d.text((x, y), text, fill=C_BLACK, font=self.font(size, bold=True))

        fx, fy = 268, Y+62

        lbl("Type / Type",                       fx,     fy)
        val("P",                                  fx,     fy+13)
        lbl("Code of issuing / Code de l'État",  fx+90,  fy)
        val("AUS",                                fx+90,  fy+13)

        fy += 48
        lbl("Name / Nom",                         fx,     fy)
        name1 = first + (" " + mid if mid else "")
        val(name1,                                fx,     fy+13)
        val(last,                                 fx,     fy+32)

        fy += 68
        lbl("Nationality / Nationalité",          fx,     fy)
        val("AUSTRALIAN",                         fx,     fy+13)

        fy += 46
        lbl("Date of birth / Date de naissance",  fx,     fy)
        val(dob.strftime("%d %b %Y").upper(),     fx,     fy+13)
        lbl("Sex / Sexe",                         fx+310, fy)
        val(sex,                                  fx+310, fy+13)

        fy += 46
        lbl("Place of birth / Lieu de naissance", fx,     fy)
        val(pob,                                  fx,     fy+13)

        fy += 46
        lbl("Date of issue / Date de délivrance", fx,     fy)
        val(issue.strftime("%d %b %Y").upper(),   fx,     fy+13)

        fy += 46
        lbl("Date of expiry / Date d'expiration", fx,     fy)
        val(expiry.strftime("%d %b %Y").upper(),  fx,     fy+13)

        fy += 46
        lbl("Authority / Autorité",               fx,     fy)
        val("CANBERRA",                           fx,     fy+13)

        # # signature
        # sx, sy = fx+310, Y+62+68+46+20
        # lbl("Holder's signature / Signature du titulaire", sx, sy-14)
        # pts = [(sx+i*15, sy + int(8*math.sin(i*1.1))) for i in range(8)]
        # d.line(pts, fill=C_BLACK, width=2)

        # MRZ
        mrz_y = H - 90
        d.rectangle([0, mrz_y-10, W, H], fill=C_MRZ_BG)
        fnt_mrz = self.font(21, bold=True)
        d.text((28, mrz_y+2),  mrz1, fill=C_BLACK, font=fnt_mrz)
        d.text((28, mrz_y+36), mrz2, fill=C_BLACK, font=fnt_mrz)