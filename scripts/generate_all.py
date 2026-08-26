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
    """Snake moves strictly orthogonally (up/down/left/right) on a grid of
    randomly-scattered contribution cells. Each cell 'appears' just before the
    snake head reaches it, then gets eaten (dimmed); the whole loop repeats."""
    import random
    random.seed(23)
    cols, rows = 50, 12
    step = 13
    cell_size = 10
    start_x, start_y = 30, 25
    dur = 22

    base_colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

    def center(c, r):
        return (start_x + c * step + cell_size // 2,
                start_y + r * step + cell_size // 2)

    # --- randomly scattered cells (not a uniform block) ---
    K = 42
    cells = []
    seen = set()
    while len(cells) < K:
        c = random.randint(0, cols - 1)
        r = random.randint(0, rows - 1)
        if (c, r) not in seen:
            seen.add((c, r))
            cells.append((c, r))

    # --- order cells by nearest-neighbour for an organic snake path ---
    order = [cells[0]]
    remaining = set(cells[1:])
    while remaining:
        cur = order[-1]
        nxt = min(remaining, key=lambda x: abs(x[0] - cur[0]) + abs(x[1] - cur[1]))
        order.append(nxt)
        remaining.discard(nxt)

    # --- build ORTHOGONAL path (only H/V segments, no diagonals) ---
    # points[2*i] = center of cell i
    points = [center(*order[0])]
    for cell in order[1:]:
        px, py = points[-1]
        tx, ty = center(*cell)
        points.append((tx, py))   # horizontal move
        points.append((tx, ty))   # vertical move

    # cumulative arc length -> eat fraction for each cell
    cum = [0.0]
    for k in range(1, len(points)):
        dx = points[k][0] - points[k - 1][0]
        dy = points[k][1] - points[k - 1][1]
        cum.append(cum[-1] + abs(dx) + abs(dy))
    total = cum[-1] or 1.0

    snake_path = "M " + " L ".join(f"{x},{y}" for x, y in points)

    # --- render scattered cells with appear + eaten behaviour ---
    cell_rects = []
    for i, (c, r) in enumerate(order):
        x = start_x + c * step
        y = start_y + r * step
        color = random.choice(base_colors)
        eat_frac = cum[2 * i] / total

        if eat_frac <= 0.004:
            base_anim = (f'<animate attributeName="opacity" values="1;0" '
                         f'keyTimes="0.985;1" dur="{dur}s" repeatCount="indefinite"/>')
            overlay_anim = (f'<animate attributeName="opacity" values="0.92;0.92;0" '
                            f'keyTimes="0;0.985;1" dur="{dur}s" repeatCount="indefinite"/>')
        elif eat_frac >= 0.999:
            # last cell: eaten right at loop end
            base_anim = (f'<animate attributeName="opacity" values="0;0;1;1;0" '
                         f'keyTimes="0;0.950;0.951;0.999;1" dur="{dur}s" repeatCount="indefinite"/>')
            overlay_anim = (f'<animate attributeName="opacity" values="0;0;0.92;0.92" '
                            f'keyTimes="0;0.9985;0.999;1" dur="{dur}s" repeatCount="indefinite"/>')
        else:
            appear = max(0.003, eat_frac - 0.05)
            base_anim = (f'<animate attributeName="opacity" values="0;0;1;1;0" '
                         f'keyTimes="0;{appear:.5f};{appear + 0.001:.5f};{eat_frac:.5f};1" '
                         f'dur="{dur}s" repeatCount="indefinite"/>')
            overlay_anim = (f'<animate attributeName="opacity" values="0;0;0.92;0.92" '
                            f'keyTimes="0;{eat_frac - 0.0005:.5f};{eat_frac:.5f};1" '
                            f'dur="{dur}s" repeatCount="indefinite"/>')

        cell_rects.append(f'''<g>
    <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="{color}" rx="2" opacity="0">{base_anim}</rect>
    <rect x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" fill="#161b22" rx="2" opacity="0">{overlay_anim}</rect>
  </g>''')

    snake_segments = 40
    snake_parts = []
    for i in range(snake_segments):
        delay = i * 0.10
        if i == 0:
            color, r = "#ff4d4d", 6.5
        elif i < 8:
            color, r = "#3fb950", 5.6 - (i * 0.12)
        else:
            color, r = "#2ea043", max(4.0, 5.6 - (i * 0.07))
        snake_parts.append(
            f'<circle cx="0" cy="0" r="{r}" fill="{color}" filter="url(#snakeGlow)">'
            f'<animateMotion path="{snake_path}" dur="{dur}s" repeatCount="indefinite" begin="{delay}s" fill="freeze" rotate="auto"/>'
            f'<animate attributeName="opacity" values="1;0.92;1" dur="1.2s" repeatCount="indefinite" begin="{delay}s"/>'
            f'</circle>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="220" viewBox="0 0 800 220">
  <defs>
    <filter id="snakeGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="800" height="220" fill="#ffffff" rx="12"/>
  <g transform="translate(62, 26)">
    {''.join(cell_rects)}
    {''.join(snake_parts)}
  </g>
</svg>'''
    generate_svg(svg, "snake.svg")

def generate_radar_scan():
    """Generate radar scan animation with cohesive binary rain background"""
    import random
    random.seed(42)
    width = 800
    height = 300
    cx, cy = 400, 160
    radius = 110
    
    # Cohesive binary rain - organized in vertical streams
    binary_drops = []
    stream_count = 24
    for i in range(stream_count):
        x = 50 + i * 30
        stream_len = random.randint(8, 15)
        for j in range(stream_len):
            char = random.choice(['0', '1'])
            y_start = -j * 22 + random.randint(-50, 0)
            duration = 3 + random.random() * 2
            delay = j * 0.15 + i * 0.08
            binary_drops.append(f'''
  <text x="{x}" y="{y_start}" fill="#00ff00" font-family="monospace" font-size="11" opacity="0.35">
    {char}
    <animate attributeName="y" from="{y_start}" to="{height + 50}" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
    <animate attributeName="opacity" values="0.4;0.7;0.1" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
  </text>''')
    
    # Radar blips (targets)
    blips = []
    blip_positions = [
        (cx + 60, cy - 40), (cx - 80, cy + 20), (cx + 30, cy + 70),
        (cx - 40, cy - 80), (cx + 90, cy + 10), (cx - 10, cy - 60)
    ]
    for idx, (bx, by) in enumerate(blip_positions):
        blips.append(f'''
  <circle cx="{bx}" cy="{by}" r="3" fill="#ff0044" opacity="0">
    <animate attributeName="opacity" values="0;1;0.8;0" dur="4s" repeatCount="indefinite" begin="{idx * 0.6}s"/>
    <animate attributeName="r" values="2;5;2" dur="2s" repeatCount="indefinite" begin="{idx * 0.6}s"/>
  </circle>''')
    
    # Sweep line with trailing glow
    sweep = f'''
  <g filter="url(#sweepGlow)">
    <path d="M {cx} {cy} L {cx} {cy - radius} A {radius} {radius} 0 0 1 {cx + radius} {cy} Z" fill="url(#radarGrad)">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="6s" repeatCount="indefinite"/>
    </path>
    <line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - radius}" stroke="#00ff00" stroke-width="2">
      <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="6s" repeatCount="indefinite"/>
    </line>
  </g>'''
    
    # Range rings with distance labels (dashed, clearly visible)
    rings = []
    for r_idx, r in enumerate([30, 60, 90, 120]):
        rings.append(f'''
  <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#00ff00" stroke-width="1.5" opacity="0.5" stroke-dasharray="7,5"/>
  <text x="{cx + r + 6}" y="{cy - 4}" fill="#00ff00" font-family="monospace" font-size="9" opacity="0.75">{r//10}0</text>''')
    
    # Crosshairs (solid, clearly visible)
    crosshairs = f'''
  <line x1="{cx - radius}" y1="{cy}" x2="{cx + radius}" y2="{cy}" stroke="#00ff00" stroke-width="0.8" opacity="0.5"/>
  <line x1="{cx}" y1="{cy - radius}" x2="{cx}" y2="{cy + radius}" stroke="#00ff00" stroke-width="0.8" opacity="0.5"/>
  <line x1="{cx - 20}" y1="{cy - 20}" x2="{cx - 5}" y2="{cy - 5}" stroke="#00ff00" stroke-width="1.5" opacity="0.7"/>
  <line x1="{cx - 20}" y1="{cy + 20}" x2="{cx - 5}" y2="{cy + 5}" stroke="#00ff00" stroke-width="1.5" opacity="0.7"/>
  <line x1="{cx + 20}" y1="{cy - 20}" x2="{cx + 5}" y2="{cy - 5}" stroke="#00ff00" stroke-width="1.5" opacity="0.7"/>
  <line x1="{cx + 20}" y1="{cy + 20}" x2="{cx + 5}" y2="{cy + 5}" stroke="#00ff00" stroke-width="1.5" opacity="0.7"/>'''
    
    # HUD elements
    hud = f'''
  <text x="20" y="30" fill="#00ff00" font-family="monospace" font-size="11" opacity="0.7">RADAR ACTIVE</text>
  <text x="20" y="50" fill="#00ff00" font-family="monospace" font-size="10" opacity="0.5">SCAN RATE: 6 RPM</text>
  <text x="20" y="70" fill="#00ff00" font-family="monospace" font-size="10" opacity="0.5">RANGE: 120 km</text>
  <text x="680" y="30" fill="#00ff00" font-family="monospace" font-size="11" opacity="0.7" text-anchor="end">TARGETS: {len(blip_positions)}</text>
  <text x="680" y="50" fill="#00ff00" font-family="monospace" font-size="10" opacity="0.5" text-anchor="end">MODE: SEARCH</text>
  <text x="680" y="70" fill="#00ff00" font-family="monospace" font-size="10" opacity="0.5" text-anchor="end">GAIN: HIGH</text>'''
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <radialGradient id="radarGrad">
      <stop offset="0%" style="stop-color:#00ff00;stop-opacity:0.4" />
      <stop offset="60%" style="stop-color:#00ff00;stop-opacity:0.15" />
      <stop offset="100%" style="stop-color:#00ff00;stop-opacity:0" />
    </radialGradient>
    <filter id="sweepGlow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="blipGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="{width}" height="{height}" fill="#050a05" rx="12"/>
  <rect x="0" y="0" width="{width}" height="{height}" fill="url(#radarGrad)" rx="12" opacity="0.02"/>
  
  {''.join(binary_drops)}
  
  {''.join(rings)}
  {crosshairs}
  {sweep}
  {''.join(blips)}
  {hud}
  
  <text x="{cx}" y="25" text-anchor="middle" font-family="Courier New" font-size="14" font-weight="600" fill="#00ff00">RADAR SCAN</text>
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
    """Generate optimized animated tech timeline with detailed milestones"""
    events = [
        ("2020", "Python & Web Dev", "🐍", "#3776AB", "Django, Flask, REST APIs"),
        ("2021", "TypeScript & React", "⚛️", "#3178C6", "Next.js, Redux, Testing"),
        ("2022", "Full-Stack & Cloud", "☁️", "#FF9900", "AWS, Docker, CI/CD, K8s"),
        ("2023", "AI/ML Engineering", "🤖", "#FF6F00", "PyTorch, LLMs, MLOps"),
        ("2024", "Systems & Rust", "🦀", "#DEA584", "Rust, WASM, Performance"),
        ("2025", "Agentic Systems", "🔮", "#8B5CF6", "Multi-Agent, RAG, Tool Use"),
    ]
    
    nodes = []
    for i, (year, title, icon, color, desc) in enumerate(events):
        x = 80 + i * 115
        
        nodes.append(f'''
  <g transform="translate({x}, 120)">
    <!-- Outer pulse ring -->
    <circle cx="0" cy="0" r="16" fill="{color}" opacity="0.15">
      <animate attributeName="r" values="14;22;14" dur="2.5s" repeatCount="indefinite" begin="{i*0.35}s"/>
      <animate attributeName="opacity" values="0.2;0.05;0.2" dur="2.5s" repeatCount="indefinite" begin="{i*0.35}s"/>
    </circle>
    <!-- Middle ring -->
    <circle cx="0" cy="0" r="12" fill="{color}" opacity="0.25">
      <animate attributeName="r" values="10;16;10" dur="2s" repeatCount="indefinite" begin="{i*0.35}s"/>
    </circle>
    <!-- Core node -->
    <circle cx="0" cy="0" r="8" fill="{color}" filter="url(#nodeGlow)">
      <animate attributeName="r" values="7;9;7" dur="1.5s" repeatCount="indefinite" begin="{i*0.35}s"/>
    </circle>
    <!-- Icon -->
    <text x="0" y="-38" text-anchor="middle" font-size="22">{icon}</text>
    <!-- Year -->
    <text x="0" y="-18" text-anchor="middle" font-family="Arial" font-size="13" font-weight="700" fill="{color}">{year}</text>
    <!-- Title -->
    <text x="0" y="2" text-anchor="middle" font-family="Arial" font-size="11" font-weight="600" fill="#333">{title}</text>
    <!-- Description -->
    <text x="0" y="16" text-anchor="middle" font-family="Arial" font-size="9" fill="#888">{desc}</text>
  </g>''')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="240" viewBox="0 0 800 240">
  <defs>
    <linearGradient id="timelineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:0.4" />
      <stop offset="20%" style="stop-color:#00d4aa;stop-opacity:0.4" />
      <stop offset="40%" style="stop-color:#F7C948;stop-opacity:0.4" />
      <stop offset="60%" style="stop-color:#ff6b9d;stop-opacity:0.4" />
      <stop offset="80%" style="stop-color:#c084fc;stop-opacity:0.4" />
      <stop offset="100%" style="stop-color:#fb923c;stop-opacity:0.4" />
    </linearGradient>
    <filter id="nodeGlow">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="lineGlow">
      <feGaussianBlur stdDeviation="1" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="800" height="240" fill="#ffffff" rx="12"/>
  
  <!-- Timeline axis with gradient -->
  <line x1="60" y1="120" x2="740" y2="120" stroke="url(#timelineGrad)" stroke-width="4" filter="url(#lineGlow)">
    <animate attributeName="stroke-dashoffset" from="0" to="-40" dur="2s" repeatCount="indefinite"/>
  </line>
  
  <!-- Subtle grid lines -->
  <g stroke="#eee" stroke-width="0.5">
    <line x1="60" y1="60" x2="740" y2="60"/>
    <line x1="60" y1="180" x2="740" y2="180"/>
  </g>
  
  {''.join(nodes)}
  
  <!-- Progress indicator -->
  <circle cx="60" cy="120" r="4" fill="#999" opacity="0.5"/>
  <circle cx="740" cy="120" r="4" fill="#999" opacity="0.5"/>
</svg>'''
    generate_svg(svg, "timeline.svg")

def generate_lang_dist():
    """Generate real-time repository language distribution from GitHub API"""
    LANG_COLORS = {
        "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Astro": "#ff5a03",
        "HTML": "#e34c26", "CSS": "#563d7c", "Python": "#3572A5",
        "Rust": "#dea584", "Go": "#00ADD8", "C++": "#f34b7d", "C": "#555555",
        "Java": "#b07219", "Shell": "#89e051", "Vue": "#41b883", "Svelte": "#ff3e00",
        "Ruby": "#701516", "PHP": "#4F5D95", "Swift": "#F05138", "Kotlin": "#A97BFF",
        "Dart": "#00B4AB", "C#": "#178600", "Jupyter Notebook": "#DA5B0B",
    }
    DEFAULT_COLOR = "#0078d4"

    repos = fetch_user_repos()
    lang_bytes = {}
    lang_repos = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        lang = repo.get("language")
        if lang:
            lang_bytes[lang] = lang_bytes.get(lang, 0) + repo.get("size", 0)
            lang_repos[lang] = lang_repos.get(lang, 0) + 1

    if not lang_bytes:
        lang_bytes = {"JavaScript": 100}
        lang_repos = {"JavaScript": 4}

    total = sum(lang_bytes.values())
    sorted_langs = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)
    top = [ (l, b) for l, b in sorted_langs if b / total >= 0.01 ][:8]
    if not top:
        top = sorted_langs[:8]

    rows = []
    y = 75
    bar_x = 270
    bar_max_w = 430
    for lang, bytes_ in top:
        pct = bytes_ / total * 100
        color = LANG_COLORS.get(lang, DEFAULT_COLOR)
        bar_w = max(6, pct / 100 * bar_max_w)
        count = lang_repos.get(lang, 0)
        rows.append(f'''
  <g transform="translate(0, {y})">
    <rect x="40" y="-10" width="14" height="14" rx="3" fill="{color}"/>
    <text x="62" y="2" font-family="Arial" font-size="14" font-weight="600" fill="#24292f">{lang}</text>
    <rect x="{bar_x}" y="-9" width="{bar_max_w}" height="12" rx="6" fill="#eaeef2"/>
    <rect x="{bar_x}" y="-9" width="{bar_w}" height="12" rx="6" fill="{color}">
      <animate attributeName="width" from="0" to="{bar_w}" dur="1s" fill="freeze"/>
    </rect>
    <text x="{bar_x + bar_max_w + 12}" y="2" font-family="Arial" font-size="13" font-weight="700" fill="{color}">{pct:.1f}%</text>
    <text x="200" y="2" text-anchor="end" font-family="Arial" font-size="11" fill="#8b949e">{count} repos</text>
  </g>''')
        y += 38

    orig_count = len(repos)
    fork_count = sum(1 for r in repos if r.get("fork"))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{y + 20}" viewBox="0 0 800 {y + 20}">
  <rect width="800" height="{y + 20}" fill="#ffffff" rx="12"/>
  <text x="400" y="40" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700" fill="#0078d4">Repository Language Distribution</text>
  {''.join(rows)}
  <text x="40" y="{y + 4}" font-family="Arial" font-size="11" fill="#8b949e">Data from {orig_count} repos ({fork_count} forks excluded) • auto-generated daily</text>
</svg>'''
    generate_svg(svg, "lang-dist.svg")

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
    generate_lang_dist()
    
    print("Generating new animation assets...")
    generate_radar_scan()
    generate_timeline()
    
    print("All assets generated!")

if __name__ == "__main__":
    main()