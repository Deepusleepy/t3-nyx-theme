import base64
import io
from pathlib import Path

import numpy as np
from PIL import Image

WIDTH, HEIGHT = 480, 270
SUPERSAMPLE = 3
SEED = 7

PALETTE_HEX = [
    "#000000", "#0b0b26", "#15174a", "#22246e", "#302f94", "#3f3cb4",
    "#4f5bd6", "#6f8cff", "#8a7fe8", "#b4aaff", "#5a35a0", "#7d45c2",
    "#a552c8", "#d06cc6", "#2a1d5c", "#eef0ff",
]

BAYER_8 = np.array([
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]) / 64 - 0.5


def hex_rgb(value: str) -> np.ndarray:
    return np.array([int(value[i:i + 2], 16) for i in (1, 3, 5)], float)


PALETTE = np.stack([hex_rgb(h) for h in PALETTE_HEX])


def lerp(a, b, t):
    t = np.clip(t, 0, 1)
    return a + (b - a) * (t[..., None] if np.ndim(t) else t)


def paint_sky() -> np.ndarray:
    ys, xs = np.mgrid[0:HEIGHT * SUPERSAMPLE, 0:WIDTH * SUPERSAMPLE]
    u = (xs + 0.5) / (WIDTH * SUPERSAMPLE)
    v = (ys + 0.5) / (HEIGHT * SUPERSAMPLE)

    glow = np.exp(-(((u - 0.62) / 0.5) ** 2 + ((v - 0.45) / 0.55) ** 2))
    img = hex_rgb("#0b0b26") * glow[..., None] * 0.9

    center = 0.78 - u * 0.72 + 0.035 * np.sin(u * 9.0) + 0.02 * np.sin(u * 23 + 1)
    width = 0.11 + 0.05 * np.sin(u * 5 + 0.7)
    d = (v - center) / width
    band = np.exp(-d * d * 0.9) * np.clip(u * 2.2, 0, 1) * np.clip((1.05 - u) * 4, 0, 1)

    stops = [(-1.8, "#2a1d5c"), (-1.0, "#8a7fe8"), (-0.35, "#b4aaff"), (0.1, "#6f8cff"),
             (0.6, "#4f5bd6"), (1.1, "#7d45c2"), (1.7, "#d06cc6"), (2.4, "#5a35a0")]
    color = np.zeros_like(img) + hex_rgb(stops[0][1])
    for (d0, c0), (d1, c1) in zip(stops, stops[1:]):
        inside = ((d >= d0) & (d < d1))[..., None]
        color = np.where(inside, lerp(hex_rgb(c0), hex_rgb(c1), (d - d0) / (d1 - d0)), color)
    color = np.where((d >= stops[-1][0])[..., None], hex_rgb(stops[-1][1]), color)

    streak = 0.75 + 0.25 * np.sin(u * 60 + v * 22) * np.sin(u * 17 + 2)
    img = lerp(img, color, band * streak * 1.15)

    curtain = np.exp(-((v - (center + 0.18)) / 0.25) ** 2) * (0.5 + 0.5 * np.sin(u * 140 + np.sin(u * 13) * 3)) ** 3
    img = lerp(img, hex_rgb("#7d45c2"), curtain * band.clip(0.15, 1) * 0.45)

    return img.reshape(HEIGHT, SUPERSAMPLE, WIDTH, SUPERSAMPLE, 3).mean(axis=(1, 3))


def dither(img: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    threshold = np.tile(BAYER_8, (HEIGHT // 8 + 1, WIDTH // 8 + 1))[:HEIGHT, :WIDTH]
    jittered = img + threshold[..., None] * 38
    indices = ((jittered[:, :, None, :] - PALETTE[None, None]) ** 2).sum(-1).argmin(-1).astype(np.uint8)

    dark = img.sum(-1) < 40
    stars = dark & (rng.random((HEIGHT, WIDTH)) < 0.0022)
    indices[stars] = rng.choice([8, 9, 15], size=stars.sum())
    for _ in range(10):
        y, x = rng.integers(3, int(HEIGHT * 0.6)), rng.integers(3, WIDTH - 3)
        if dark[y, x]:
            indices[y, x] = 15
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                indices[y + dy, x + dx] = 9
    return indices


def encode_webp(indices: np.ndarray) -> bytes:
    image = Image.fromarray(indices, "P")
    image.putpalette([int(c) for rgb in PALETTE for c in rgb])
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, "WEBP", lossless=True, quality=100, method=6, exact=True)
    return buffer.getvalue()


def build_art_data_url() -> str:
    webp = encode_webp(dither(paint_sky()))
    return "data:image/webp;base64," + base64.b64encode(webp).decode()


if __name__ == "__main__":
    out = Path(__file__).parent / "build" / "art.webp"
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(encode_webp(dither(paint_sky())))
    print(out)
