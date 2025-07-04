#!/usr/bin/env python3
"""
Generate PNG favicon files from SVG for Ethical Capital
"""
from pathlib import Path
import subprocess

# Check if we have required tools
def check_dependencies():
    """Check if required tools are installed"""
    try:
        # Try cairosvg first (preferred)
        import cairosvg  # noqa: F401
        return 'cairosvg'
    except ImportError:
        # Check for rsvg-convert command
        result = subprocess.run(['which', 'rsvg-convert'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'rsvg'
        
        # Check for ImageMagick convert
        result = subprocess.run(['which', 'convert'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'imagemagick'
    
    return None

def generate_pngs():
    """Generate PNG files from SVG"""
    base_dir = Path('/Users/srvo/ethicic-public/static')
    svg_file = base_dir / 'favicon.svg'
    
    if not svg_file.exists():
        print(f"❌ SVG file not found: {svg_file}")
        return False
    
    # Files to generate
    files_to_generate = [
        ('android-chrome-192x192.png', 192),
        ('android-chrome-512x512.png', 512),
        ('apple-touch-icon.png', 180),
    ]
    
    converter = check_dependencies()
    
    if converter is None:
        print("❌ No SVG converter found. Please install one of:")
        print("   - pip install cairosvg")
        print("   - brew install librsvg")
        print("   - brew install imagemagick")
        return False
    
    print(f"✅ Using {converter} to convert SVG to PNG")
    
    for filename, size in files_to_generate:
        output_file = base_dir / filename
        
        try:
            if converter == 'cairosvg':
                import cairosvg
                cairosvg.svg2png(
                    url=str(svg_file),
                    write_to=str(output_file),
                    output_width=size,
                    output_height=size
                )
            elif converter == 'rsvg':
                subprocess.run([
                    'rsvg-convert',
                    '-w', str(size),
                    '-h', str(size),
                    str(svg_file),
                    '-o', str(output_file)
                ], check=True)
            elif converter == 'imagemagick':
                subprocess.run([
                    'convert',
                    '-background', 'none',
                    '-resize', f'{size}x{size}',
                    str(svg_file),
                    str(output_file)
                ], check=True)
            
            print(f"✅ Generated: {filename} ({size}x{size})")
        except Exception as e:
            print(f"❌ Failed to generate {filename}: {e}")
            
            # Try a fallback method using PIL
            try:
                from PIL import Image, ImageDraw
                
                # Create a purple background with white E
                img = Image.new('RGBA', (size, size), (85, 60, 154, 255))  # #553C9A
                draw = ImageDraw.Draw(img)
                
                # Draw a simple E (basic fallback)
                margin = size // 8
                line_width = size // 16
                
                # Vertical line of E
                draw.rectangle([margin, margin, margin + line_width, size - margin], fill='white')
                
                # Three horizontal lines of E
                # Top
                draw.rectangle([margin, margin, size - margin, margin + line_width], fill='white')
                # Middle
                mid = size // 2
                draw.rectangle([margin, mid - line_width//2, size - margin - margin, mid + line_width//2], fill='white')
                # Bottom
                draw.rectangle([margin, size - margin - line_width, size - margin, size - margin], fill='white')
                
                img.save(output_file, 'PNG')
                print(f"✅ Generated {filename} using fallback method")
            except ImportError:
                print(f"⚠️  Could not generate {filename} - install Pillow: pip install Pillow")
    
    return True

if __name__ == '__main__':
    generate_pngs()
