#!/usr/bin/env python3
"""
Generate all profile assets locally for GitHub README
Run via GitHub Actions, saves static files to assets/
"""

import os
import requests
from datetime import datetime
from pathlib import Path

ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "noontiger"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def fetch_github_api(url):
    results = []
    while url:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        results.extend(resp.json())
        url = resp.links.get("next", {}).get("url")
    return results

def fetch_user_repos():
    try:
        repos = fetch_github_api(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner")
        return repos if repos else []
    except Exception:
        return []

def fetch_user_stats():
    try:
        resp = requests.get(f"https://api.github.com/users/{USERNAME}", headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return {"followers": 0, "following": 0, "public_repos": 0, "created_at": "2020-01-01T00:00:00Z"}

def generate_svg(content, filename):
    path = ASSETS_DIR / filename
    path.write_text(content, encoding="utf-8")
    print(f"Generated: {path}")

# ==================== EXISTING FUNCTIONS ====================

def generate_snake():
    cols = 53
    rows = 7
    cell_size = 11
    gap = 3
    start_x = 25
    start_y = 40
    
    squares = []
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * (cell_size + gap)
            y = start_y + r * (cell_size + gap)
            level = ((r * 13 + c * 7) % 5)
            colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
            color = colors[level]
            squares.append(
                f'<rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2"/>'
            )
    
    path_points = []
    for c in range(cols):
        r = c % rows
        x = start_x + c * (cell_size + gap) + cell_size // 2
        y = start_y + r * (cell_size + gap) + cell_size // 2
        path_points.append(f"{x},{y}")
    
    snake_path = "M " + " L ".join(path_points)
    
    snake_segments = 35
    snake_parts = []
    for i in range(snake_segments):
        progress = 1 - (i / snake_segments)
        color = "#ff6b6b" if i == 0 else ("#40c463" if i < 5 else "#30a14e")
        r = 6 if i == 0 else (5 if i < 5 else 4)
        snake_parts.append(
            f'<circle cx="0" cy="0" r="{r}" fill="{color}">'
            f'<animateMotion path="{snake_path}" dur="12s" repeatCount="indefinite" begin="{i * 0.15}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;0.8;1" dur="1.5s" repeatCount="indefinite" begin="{i * 0.1}s"/>'
            f'</circle>'
        )
    
    eaten_highlights = []
    for c in range(0, cols, 2):
        r = c % rows
        x = start_x + c * (cell_size + gap) + cell_size // 2
        y = start_y + r * (cell_size + gap) + cell_size // 2
        eaten_highlights.append(
            f'<circle cx="{x}" cy="{y}" r="{cell_size//2}" fill="#ff6b6b" opacity="0.3">'
            f'<animate attributeName="opacity" values="0.3;0.6;0.3" dur="2s" repeatCount="indefinite" begin="{c * 0.1}s"/>'
            f'</circle>'
        )
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <rect width="800" height="200" fill="#ffffff" rx="12"/>
  <g transform="translate(0, 10)">
    {''.join(squares)}
    {''.join(eaten_highlights)}
    {''.join(snake_parts)}
  </g>
</svg>'''
    generate_svg(svg, "snake.svg")

def generate_radar_scan():
    """Generate radar scan animation with matrix rain background"""
    import random
    width = 800
    height = 300
    binary_drops = []
    columns = 40
    for i in range(columns):
        x = i * 20
        for _ in range(3):
            char = random.choice(['0', '1'])
            duration = 1.5 + random.random() * 2
            delay = random.random() * 4
            binary_drops.append(f'''
  <text x="{x + random.randint(-2, 2)}" y="20" fill="#00ff00" font-family="monospace" font-size="12" opacity="0.4">
    {char}
    <animate attributeName="y" from="0" to="{height}" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
    <animate attributeName="opacity" values="0.6;0.1" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
  </text>''')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <radialGradient id="radarGrad">
      <stop offset="0%" style="stop-color:#00ff00;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#00ff00;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="{width}" height="{height}" fill="#0a0a0a" rx="8"/>
  {''.join(binary_drops)}
  <text x="400" y="25" text-anchor="middle" font-family="Courier New" font-size="16" font-weight="600" fill="#00ff00">Radar Scan</text>
  
  <circle cx="400" cy="160" r="100" fill="none" stroke="#00ff00" stroke-width="1" opacity="0.3"/>
  <circle cx="400" cy="160" r="75" fill="none" stroke="#00ff00" stroke-width="1" opacity="0.3"/>
  <circle cx="400" cy="160" r="50" fill="none" stroke="#00ff00" stroke-width="1" opacity="0.3"/>
  <circle cx="400" cy="160" r="25" fill="none" stroke="#00ff00" stroke-width="1" opacity="0.3"/>
  <line x1="400" y1="60" x2="400" y2="260" stroke="#00ff00" stroke-width="1" opacity="0.3"/>
  <line x1="300" y1="160" x2="500" y2="160" stroke="#00ff00" stroke-width="1" opacity="0.3"/>
  
  <path d="M 400 160 L 400 60 A 100 100 0 0 1 500 160 Z" fill="url(#radarGrad)">
    <animateTransform attributeName="transform" type="rotate" from="0 400 160" to="360 400 160" dur="4s" repeatCount="indefinite"/>
  </path>
  
  <circle cx="450" cy="120" r="4" fill="#00ff00">
    <animate attributeName="opacity" values="0;1;0" dur="4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="380" cy="180" r="3" fill="#00ff00">
    <animate attributeName="opacity" values="0;1;0" dur="4s" repeatCount="indefinite" begin="1s"/>
  </circle>
</svg>'''
    generate_svg(svg, "radar-scan.svg")

def generate_terminal():
    """Generate terminal typing animation"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <rect width="800" height="300" fill="#1e1e1e" rx="8"/>
  <rect x="10" y="10" width="780" height="30" fill="#2d2d2d" rx="4"/>
  <circle cx="25" cy="25" r="8" fill="#ff5f56"/>
  <circle cx="45" cy="25" r="8" fill="#ffbd2e"/>
  <circle cx="65" cy="25" r="8" fill="#27c93f"/>
  
  <text x="20" y="80" font-family="Courier New" font-size="14" fill="#00ff00">$ whoami</text>
  <text x="20" y="110" font-family="Courier New" font-size="14" fill="#ffffff">noontiger</text>
  <text x="20" y="150" font-family="Courier New" font-size="14" fill="#00ff00">$ cat skills.txt</text>
  <text x="20" y="180" font-family="Courier New" font-size="14" fill="#ff00ff">Python, JavaScript, TypeScript, Rust, Go...</text>
  <text x="20" y="220" font-family="Courier New" font-size="14" fill="#00ffff">$ ./build_awesome.sh</text>
  <text x="20" y="250" font-family="Courier New" font-size="14" fill="#ffff00">Building the future...</text>
  
  <rect x="20" y="255" width="10" height="20" fill="#00ff00">
    <animate attributeName="opacity" values="1;0" dur="0.5s" repeatCount="indefinite"/>
  </rect>
</svg>'''
    generate_svg(svg, "terminal.svg")

def generate_circuit_board():
    """Generate optimized circuit board pattern with glow effects and data flow"""
    nodes = [
        (100, 80), (250, 120), (400, 60), (550, 140), (700, 100),
        (150, 180), (300, 160), (450, 200), (600, 180), (750, 220)
    ]
    
    lines = [
        (100, 80, 250, 120), (250, 120, 400, 60), (400, 60, 550, 140),
        (550, 140, 700, 100), (150, 180, 300, 160), (300, 160, 450, 200),
        (450, 200, 600, 180), (600, 180, 750, 220), (250, 120, 300, 160),
        (400, 60, 450, 200), (550, 140, 600, 180), (100, 80, 150, 180)
    ]
    
    circuit_lines = []
    for x1, y1, x2, y2 in lines:
        circuit_lines.append(f'''
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#0078d4" stroke-width="2" opacity="0.6">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="3s" repeatCount="indefinite"/>
  </line>''')
    
    circuit_nodes = []
    for i, (x, y) in enumerate(nodes):
        color = "#00d4aa" if i % 2 == 0 else "#0078d4"
        circuit_nodes.append(f'''
  <circle cx="{x}" cy="{y}" r="6" fill="{color}" opacity="0.8">
    <animate attributeName="r" values="5;8;5" dur="2s" repeatCount="indefinite" begin="{i*0.2}s"/>
    <animate attributeName="opacity" values="0.6;1;0.6" dur="2s" repeatCount="indefinite" begin="{i*0.2}s"/>
  </circle>''')
    
    data_packets = []
    for i, (x1, y1, x2, y2) in enumerate(lines[:4]):
        data_packets.append(f'''
  <circle cx="0" cy="0" r="3" fill="#F7C948">
    <animateMotion path="M {x1},{y1} L {x2},{y2}" dur="2s" repeatCount="indefinite" begin="{i*0.5}s"/>
    <animate attributeName="opacity" values="0;1;0" dur="2s" repeatCount="indefinite" begin="{i*0.5}s"/>
  </circle>''')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="280" viewBox="0 0 800 280">
  <defs>
    <linearGradient id="circuitGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#00d4aa;stop-opacity:0.8" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="800" height="280" fill="#0a0a0a" rx="12"/>
  
  {''.join(circuit_lines)}
  {''.join(circuit_nodes)}
  {''.join(data_packets)}
  
  <text x="400" y="260" text-anchor="middle" font-family="Courier New" font-size="12" fill="#0078d4" filter="url(#glow)">⚡ Data flows through circuits...</text>
</svg>'''
    generate_svg(svg, "circuit-board.svg")

def generate_particles():
    """Generate optimized particle network with connections and dynamic motion"""
    particles = []
    connections = []
    
    for i in range(25):
        x = 80 + (i % 5) * 150 + (i % 3) * 20
        y = 60 + (i // 5) * 120 + (i % 2) * 30
        size = 2 + (i % 4)
        duration = 3 + (i % 3)
        delay = i * 0.15
        
        particles.append(f'''
  <circle cx="{x}" cy="{y}" r="{size}" fill="#0078d4">
    <animate attributeName="opacity" values="0.4;1;0.4" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
    <animate attributeName="r" values="{size};{size+2};{size}" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
  </circle>''')
        
        for j in range(i + 1, min(i + 4, 25)):
            x2 = 80 + (j % 5) * 150 + (j % 3) * 20
            y2 = 60 + (j // 5) * 120 + (j % 2) * 30
            dist = ((x - x2) ** 2 + (y - y2) ** 2) ** 0.5
            if dist < 200:
                connections.append(f'''
  <line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="#0078d4" stroke-width="1" opacity="0.2">
    <animate attributeName="opacity" values="0.1;0.4;0.1" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
  </line>''')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="320" viewBox="0 0 800 320">
  <defs>
    <radialGradient id="particleGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#0078d4;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="800" height="320" fill="#0a0a0a" rx="12"/>
  <rect x="0" y="0" width="800" height="320" fill="url(#particleGlow)" rx="12"/>
  
  {''.join(connections)}
  {''.join(particles)}
  
  <text x="400" y="300" text-anchor="middle" font-family="Courier New" font-size="11" fill="#0078d4">🤖 Neural network visualization</text>
</svg>'''
    generate_svg(svg, "particles.svg")

def generate_timeline():
    """Generate optimized animated tech timeline with icons and gradients"""
    events = [
        ("2020", "Started Coding", "💻", "#0078d4"),
        ("2021", "First Open Source", "🌟", "#00d4aa"),
        ("2022", "Full-Stack Dev", "🚀", "#F7C948"),
        ("2023", "AI/ML Explorer", "🤖", "#ff6b9d"),
        ("2024", "Cloud Native", "☸️", "#c084fc"),
        ("2025", "Building Future", "🔮", "#fb923c")
    ]
    
    nodes = []
    for i, (year, event, icon, color) in enumerate(events):
        x = 100 + i * 120
        
        nodes.append(f'''
  <g transform="translate({x}, 120)">
    <circle cx="0" cy="0" r="12" fill="{color}" opacity="0.2">
      <animate attributeName="r" values="10;16;10" dur="2s" repeatCount="indefinite" begin="{i*0.3}s"/>
    </circle>
    <circle cx="0" cy="0" r="8" fill="{color}">
      <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite" begin="{i*0.3}s"/>
    </circle>
    <text x="0" y="-25" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700" fill="{color}">{year}</text>
    <text x="0" y="35" text-anchor="middle" font-family="Arial" font-size="11" fill="#666">{event}</text>
  </g>''')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="220" viewBox="0 0 800 220">
  <defs>
    <linearGradient id="timelineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:0.3" />
      <stop offset="50%" style="stop-color:#00d4aa;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#0078d4;stop-opacity:0.3" />
    </linearGradient>
    <filter id="nodeGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="800" height="220" fill="#ffffff" rx="12"/>
  
  <line x1="80" y1="120" x2="720" y2="120" stroke="url(#timelineGrad)" stroke-width="3" stroke-dasharray="8,4">
    <animate attributeName="stroke-dashoffset" from="0" to="-24" dur="1s" repeatCount="indefinite"/>
  </line>
  
  {''.join(nodes)}
</svg>'''
    generate_svg(svg, "timeline.svg")

def generate_wakatime():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="250" viewBox="0 0 800 250">
  <rect width="800" height="250" fill="#ffffff" rx="12"/>
  <text x="400" y="35" text-anchor="middle" font-family="Arial" font-size="18" font-weight="600" fill="#0078d4">WakaTime Stats</text>
  
  <g transform="translate(100, 70)">
    <rect width="600" height="140" fill="#f8f9fa" rx="8"/>
    <text x="300" y="40" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">Total Coding Time</text>
    <text x="300" y="80" text-anchor="middle" font-family="Arial" font-size="36" font-weight="bold" fill="#0078d4">1,234</text>
    <text x="300" y="105" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">hours this year</text>
    <text x="300" y="130" text-anchor="middle" font-family="Arial" font-size="12" fill="#999">Python • JavaScript • TypeScript • Rust</text>
  </g>
</svg>'''
    generate_svg(svg, "wakatime.svg")

# ==================== MAIN ====================

def main():
    print("Generating profile assets...")
    generate_snake()
    generate_wakatime()
    
    print("Generating new animation assets...")
    generate_radar_scan()
    generate_timeline()
    
    print("All assets generated!")

if __name__ == "__main__":
    main()