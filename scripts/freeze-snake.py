"""Freeze generated SVG at its initial contribution state for reduced-motion users."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

source = Path('assets/snake.svg').read_text(encoding='utf-8')
# Keep base cell fills; disable CSS motion without changing contribution data.
override = '<style>*{animation:none!important;transition:none!important}</style>'
source = re.sub(r'<(?:animate|animateTransform|animateMotion|set)\b[^>]*/>', '', source)
source = source.replace('</svg>', override + '</svg>')
ET.fromstring(source)
Path('assets/snake-static.svg').write_text(source, encoding='utf-8')
