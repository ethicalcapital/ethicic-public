#!/usr/bin/env python3
"""
Generate social media PNG files from SVG for Ethical Capital
"""
import subprocess
from pathlib import Path


def generate_social_pngs():
    """Generate social media PNG files from SVG"""
    base_dir = Path("/Users/srvo/ethicic-public/static/images")

    # Files to generate
    conversions = [
        ("og-default.svg", "og-default.png", 1200, 630),
        ("twitter-card.svg", "twitter-card.png", 1200, 600),
    ]

    for svg_name, png_name, width, height in conversions:
        svg_file = base_dir / svg_name
        png_file = base_dir / png_name

        if not svg_file.exists():
            print(f"❌ SVG file not found: {svg_file}")
            continue

        try:
            # Use rsvg-convert
            subprocess.run([
                "rsvg-convert",
                "-w", str(width),
                "-h", str(height),
                str(svg_file),
                "-o", str(png_file)
            ], check=True)

            print(f"✅ Generated: {png_name} ({width}x{height})")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate {png_name}: {e}")

            # Try ImageMagick as fallback
            try:
                subprocess.run([
                    "convert",
                    "-background", "none",
                    "-resize", f"{width}x{height}!",
                    str(svg_file),
                    str(png_file)
                ], check=True)
                print(f"✅ Generated {png_name} using ImageMagick")
            except Exception as e:
                print(f"⚠️  Could not generate {png_name}: {e}")

if __name__ == "__main__":
    generate_social_pngs()
