#!/usr/bin/env python3
"""
Garden UI CSS Bundle Builder
Creates optimized CSS bundles for production deployment

Usage:
    python scripts/build_css.py [--development] [--minify]
    
Options:
    --development   Build development bundle with comments and debugging info
    --minify        Minify the output (requires csso or similar tool)
    --watch         Watch for file changes and rebuild automatically
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add Django project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class CSSBundler:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.css_dir = self.project_root / "static" / "css"
        self.output_dir = self.css_dir / "bundles"
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
        
        # Define bundle configurations
        self.bundles = {
            "garden-ui-foundation.css": [
                "garden-ui-layers.css",
                "garden-ui-advanced-layers.css", 
                "garden-ui-tokens.css"
            ],
            "garden-ui-core.css": [
                "garden-ui-panels.css",
                "garden-ui-buttons.css", 
                "garden-ui-forms.css",
                "garden-ui-typography.css",
                "garden-ui-layout.css",
                "garden-ui-core.css"
            ],
            "garden-ui-layout.css": [
                "garden-ui-responsive.css",
                "garden-ui-header.css",
                "garden-ui-navigation.css", 
                "garden-ui-footer.css"
            ],
            "garden-ui-complete.css": [
                # Complete bundle - all modular files
                "garden-ui-layers.css",
                "garden-ui-advanced-layers.css",
                "garden-ui-tokens.css",
                "garden-ui-panels.css", 
                "garden-ui-buttons.css",
                "garden-ui-forms.css",
                "garden-ui-typography.css",
                "garden-ui-layout.css",
                "garden-ui-core.css",
                "garden-ui-responsive.css",
                "garden-ui-header.css",
                "garden-ui-navigation.css",
                "garden-ui-footer.css"
            ]
        }
        
    def read_css_file(self, filename):
        """Read CSS file and return content with metadata"""
        file_path = self.css_dir / filename
        
        if not file_path.exists():
            print(f"⚠️  Warning: File not found: {filename}")
            return ""
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Get file stats
            stat = file_path.stat()
            size_kb = stat.st_size / 1024
            
            print(f"📁 {filename} ({size_kb:.1f}KB)")
            return content
            
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")
            return ""
    
    def create_bundle_header(self, bundle_name, files, development=False):
        """Create informative header for bundle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = f"""/*!
 * {bundle_name} - Garden UI CSS Bundle
 * Generated: {timestamp}
 * 
 * This bundle combines the following modular CSS files:
"""
        
        for file in files:
            header += f" * - {file}\n"
            
        header += " *\n"
        header += " * CSS Layers Architecture:\n"
        header += " * @layer reset, tokens, themes, base, components, utilities;\n"
        header += " *\n"
        header += " * For development, use individual modular files.\n"
        header += " * For production, use this optimized bundle.\n"
        header += " */\n\n"
        
        if development:
            header += "/* ===== DEVELOPMENT BUILD ===== */\n"
            header += "/* Source maps and comments preserved for debugging */\n\n"
        
        return header
    
    def optimize_css(self, content, development=False):
        """Basic CSS optimization"""
        if development:
            return content
            
        # Basic optimizations (can be extended with proper CSS minifier)
        optimized = content
        
        # Remove excessive whitespace (preserve within strings)
        import re
        
        # Remove comments (except special ones like /*! */)
        optimized = re.sub(r'/\*(?!\!).*?\*/', '', optimized, flags=re.DOTALL)
        
        # Remove extra whitespace
        optimized = re.sub(r'\n\s*\n', '\n', optimized)
        optimized = re.sub(r'  +', ' ', optimized)
        
        # Remove trailing whitespace
        optimized = re.sub(r' +\n', '\n', optimized)
        
        return optimized.strip()
    
    def create_bundle(self, bundle_name, files, development=False):
        """Create a CSS bundle from multiple files"""
        print(f"\n🔨 Building {bundle_name}...")
        
        # Create bundle header
        content = self.create_bundle_header(bundle_name, files, development)
        
        # Add section separator
        content += f"/* ===== BUNDLE CONTENTS ===== */\n\n"
        
        total_size = 0
        
        # Process each file
        for file in files:
            file_content = self.read_css_file(file)
            
            if file_content:
                # Add file separator in development mode
                if development:
                    content += f"/* ================================================\n"
                    content += f" * FILE: {file}\n"
                    content += f" * ================================================ */\n\n"
                
                content += file_content
                content += "\n\n"
                
                # Calculate size
                total_size += len(file_content.encode('utf-8'))
        
        # Optimize content
        if not development:
            print("🔧 Optimizing CSS...")
            content = self.optimize_css(content, development)
        
        # Write bundle
        output_path = self.output_dir / bundle_name
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Get final size
            final_size = output_path.stat().st_size
            final_size_kb = final_size / 1024
            original_size_kb = total_size / 1024
            
            if not development and total_size > 0:
                savings = ((total_size - final_size) / total_size) * 100
                print(f"📦 Bundle created: {bundle_name}")
                print(f"   Original: {original_size_kb:.1f}KB")
                print(f"   Optimized: {final_size_kb:.1f}KB")
                print(f"   Savings: {savings:.1f}%")
            else:
                print(f"📦 Bundle created: {bundle_name} ({final_size_kb:.1f}KB)")
                
        except Exception as e:
            print(f"❌ Error writing bundle {bundle_name}: {e}")
    
    def build_all(self, development=False):
        """Build all CSS bundles"""
        print("🚀 Starting Garden UI CSS Bundle Build")
        print(f"📂 Source directory: {self.css_dir}")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"🔧 Mode: {'Development' if development else 'Production'}")
        
        start_time = time.time()
        
        # Build each bundle
        for bundle_name, files in self.bundles.items():
            self.create_bundle(bundle_name, files, development)
        
        # Create manifest file
        self.create_manifest()
        
        elapsed = time.time() - start_time
        print(f"\n✅ Build completed in {elapsed:.2f}s")
        print(f"📁 Bundles available in: {self.output_dir}")
        
    def create_manifest(self):
        """Create a manifest file with bundle information"""
        manifest = {
            "bundles": {},
            "generated": datetime.now().isoformat(),
            "source_directory": str(self.css_dir),
            "modular_files": []
        }
        
        # Add bundle information
        for bundle_name, files in self.bundles.items():
            bundle_path = self.output_dir / bundle_name
            
            if bundle_path.exists():
                stat = bundle_path.stat()
                manifest["bundles"][bundle_name] = {
                    "files": files,
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 1),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
        
        # Add modular file list
        for css_file in self.css_dir.glob("garden-ui-*.css"):
            if css_file.name not in ["garden-ui-public.css"]:  # Skip legacy files
                manifest["modular_files"].append(css_file.name)
        
        # Write manifest
        import json
        manifest_path = self.output_dir / "manifest.json"
        
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            print(f"📄 Manifest created: {manifest_path.name}")
        except Exception as e:
            print(f"❌ Error creating manifest: {e}")
    
    def watch_files(self, development=False):
        """Watch for file changes and rebuild automatically"""
        print("👀 Watching for file changes...")
        print("Press Ctrl+C to stop")
        
        try:
            import watchdog
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            print("❌ Watchdog not installed. Install with: pip install watchdog")
            return
        
        class CSSFileHandler(FileSystemEventHandler):
            def __init__(self, bundler, development):
                self.bundler = bundler
                self.development = development
                self.last_build = 0
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                    
                if event.src_path.endswith('.css'):
                    # Debounce rapid changes
                    now = time.time()
                    if now - self.last_build < 1:
                        return
                        
                    print(f"\n🔄 File changed: {Path(event.src_path).name}")
                    self.bundler.build_all(self.development)
                    self.last_build = now
        
        event_handler = CSSFileHandler(self, development)
        observer = Observer()
        observer.schedule(event_handler, str(self.css_dir), recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            print("\n👋 Stopping file watcher...")
        observer.join()

def main():
    parser = argparse.ArgumentParser(description="Garden UI CSS Bundle Builder")
    parser.add_argument("--development", action="store_true", 
                       help="Build development bundle with comments")
    parser.add_argument("--minify", action="store_true",
                       help="Minify the output (basic optimization)")
    parser.add_argument("--watch", action="store_true",
                       help="Watch for file changes and rebuild")
    
    args = parser.parse_args()
    
    # Initialize bundler
    bundler = CSSBundler(project_root)
    
    if args.watch:
        # Build once, then watch
        bundler.build_all(args.development)
        bundler.watch_files(args.development)
    else:
        # Single build
        bundler.build_all(args.development)

if __name__ == "__main__":
    main()