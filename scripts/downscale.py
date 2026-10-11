#!/usr/bin/env python3
"""Downscale screenshots to JPEG ~900px wide for vision_analyze.

The vision provider rejects large PNGs; PIL downscale to JPEG 900px, q85
fixes it (validated in the Match-3D.js workflow).

Usage: python3 scripts/downscale.py <in.png> [out.jpg]
"""
import sys
from PIL import Image

def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else src.rsplit('.', 1)[0] + '_qa.jpg'
    img = Image.open(src).convert('RGB')
    w, h = img.size
    if w > 900:
        img = img.resize((900, int(h * 900 / w)), Image.LANCZOS)
    img.save(out, 'JPEG', quality=85)
    print(out)

if __name__ == '__main__':
    main()
