"""Helpers for the users app, namely default avatar generation."""

import random
import uuid
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont

from users import constants


def _load_font(size):
    """Load the bundled display font, falling back to Pillow's default."""
    font_path = Path(settings.BASE_DIR) / "static" / constants.AVATAR_FONT_PATH
    try:
        return ImageFont.truetype(str(font_path), size=size)
    except OSError:
        return ImageFont.load_default(size=size)


def generate_avatar(name):
    """Generate a square avatar with the first letter of ``name``.

    The letter is drawn in white, centered on a solid, calmly coloured
    background picked at random from a curated palette. Returns a
    ``ContentFile`` ready to be assigned to an ``ImageField``.
    """
    letter = (name[:1] or constants.AVATAR_FALLBACK_LETTER).upper()
    background = random.choice(constants.AVATAR_BACKGROUND_COLORS)

    size = constants.AVATAR_SIZE
    image = Image.new("RGB", (size, size), background)
    draw = ImageDraw.Draw(image)
    font = _load_font(int(size * constants.AVATAR_FONT_RATIO))

    # Center the glyph using its bounding box (accounts for font metrics).
    left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
    x = (size - (right - left)) / 2 - left
    y = (size - (bottom - top)) / 2 - top
    draw.text((x, y), letter, font=font, fill=constants.AVATAR_TEXT_COLOR)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"avatar_{uuid.uuid4().hex}.png")
