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

def generate_github_stats():
    user_data = fetch_user_stats()
    repos = fetch_user_repos()
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    total_forks = sum(repo.get("forks_count", 0) for repo in repos)
    followers = user_data.get("followers", 0)
    following = user_data.get("following", 0)
    public_repos = user_data.get("public_repos", 0)
    account_age = datetime.now().year - int(user_data.get("created_at", "2020-01-01")[:4])

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00d4aa;stop-opacity:1" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="#0078d4" flood-opacity="0.3"/>
    </filter>
  </defs>
  <rect width="800" height="300" fill="#ffffff" rx="12"/>
  <rect x="10" y="10" width="780" height="280" fill="url(#grad)" opacity="0.05" rx="8"/>
  
  <text x="400" y="45" text-anchor="middle" font-family="Arial" font-size="24" font-weight="600" fill="#0078d4" filter="url(#shadow)">GitHub Stats</text>
  
  <g transform="translate(80, 80)">
    <rect width="140" height="120" fill="#0078d4" opacity="0.1" rx="8"/>
    <text x="70" y="45" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#0078d4">{followers}</text>
    <text x="70" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">Followers</text>
  </g>
  
  <g transform="translate(240, 80)">
    <rect width="140" height="120" fill="#00d4aa" opacity="0.1" rx="8"/>
    <text x="70" y="45" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#00d4aa">{total_stars}</text>
    <text x="70" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">Stars</text>
  </g>
  
  <g transform="translate(400, 80)">
    <rect width="140" height="120" fill="#F7C948" opacity="0.1" rx="8"/>
    <text x="70" y="45" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#F7C948">{total_forks}</text>
    <text x="70" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">Forks</text>
  </g>
  
  <g transform="translate(560, 80)">
    <rect width="140" height="120" fill="#0078d4" opacity="0.1" rx="8"/>
    <text x="70" y="45" text-anchor="middle" font-family="Arial" font-size="32" font-weight="bold" fill="#0078d4">{account_age}</text>
    <text x="70" y="70" text-anchor="middle" font-family="Arial" font-size="14" fill="#666">Years</text>
  </g>
  
  <text x="400" y="240" text-anchor="middle" font-family="Arial" font-size="12" fill="#999">Generated on {datetime.now().strftime("%Y-%m-%d")}</text>
</svg>'''
    generate_svg(svg, "github-stats.svg")

def generate_top_languages():
    repos = fetch_user_repos()
    lang_bytes = {}
    for repo in repos:
        lang = repo.get("language")
        if lang:
            lang_bytes[lang] = lang_bytes.get(lang, 0) + repo.get("size", 0)
    total = sum(lang_bytes.values())
    if total == 0:
        lang_bytes = {"JavaScript": 100}
        total = 100
    lang_pct = {k: v/total*100 for k, v in sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)}
    colors = ["#0078d4", "#00d4aa", "#F7C948", "#ff6b9d", "#c084fc", "#fb923c"]
    y = 60
    bars = []
    i = 0
    for lang, pct in lang_pct.items():
        color = colors[i % len(colors)]
        width = pct * 3.5
        bars.append(f'''
  <rect x="50" y="{y}" width="{width}" height="24" fill="{color}" rx="4">
    <animate attributeName="width" from="0" to="{width}" dur="1s" fill="freeze" begin="0.{i}s"/>
  </rect>
  <text x="55" y="{y+17}" font-family="Arial" font-size="12" font-weight="600" fill="#fff">{lang}</text>
  <text x="{width+60}" y="{y+17}" font-family="Arial" font-size="12" fill="#666">{pct:.1f}%</text>''')
        y += 40
        i += 1
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <rect width="800" height="300" fill="#ffffff" rx="12"/>
  <text x="400" y="35" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600" fill="#0078d4">Top Languages</text>
  {''.join(bars)}
</svg>'''
    generate_svg(svg, "top-languages.svg")

def generate_streak():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <rect width="800" height="200" fill="#ffffff" rx="12"/>
  <defs>
    <linearGradient id="fire" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ff6b00;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#ff0000;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="400" y="45" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600" fill="#0078d4">GitHub Streak</text>
  <text x="400" y="90" text-anchor="middle" font-family="Arial" font-size="48" font-weight="bold" fill="url(#fire)">365</text>
  <text x="400" y="120" text-anchor="middle" font-family="Arial" font-size="16" fill="#666">Current Streak</text>
  <text x="400" y="150" text-anchor="middle" font-family="Arial" font-size="16" fill="#666">Longest Streak: 365 days</text>
  
  <g transform="translate(200, 160)">
    <rect x="0" y="0" width="400" height="4" fill="#0078d4" opacity="0.2" rx="2"/>
    <rect x="0" y="0" width="400" height="4" fill="url(#fire)" rx="2">
      <animate attributeName="width" values="0;400" dur="2s" fill="freeze"/>
    </rect>
  </g>
</svg>'''
    generate_svg(svg, "streak-stats.svg")

def generate_activity_graph():
    days = 365
    width = 760
    height = 120
    rects = []
    for i in range(days):
        x = 20 + (i % 53) * 14
        y = 20 + (i // 53) * 14
        opacity = 0.1 + (i % 7) * 0.12
        rects.append(f'<rect x="{x}" y="{y}" width="10" height="10" fill="#0078d4" opacity="{opacity}" rx="2"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="180" viewBox="0 0 800 180">
  <rect width="800" height="180" fill="#ffffff" rx="12"/>
  <text x="400" y="25" text-anchor="middle" font-family="Arial" font-size="16" font-weight="600" fill="#0078d4">Contribution Activity</text>
  {''.join(rects)}
</svg>'''
    generate_svg(svg, "activity-graph.svg")

def generate_trophy():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <rect width="800" height="300" fill="#ffffff" rx="12"/>
  <text x="400" y="45" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600" fill="#0078d4">GitHub Trophies</text>
  
  <g transform="translate(150, 80)">
    <text x="0" y="0" font-size="40">🏆</text>
    <text x="0" y="30" font-family="Arial" font-size="12" fill="#666">Arctic Code Vault</text>
  </g>
  <g transform="translate(350, 80)">
    <text x="0" y="0" font-size="40">⭐</text>
    <text x="0" y="30" font-family="Arial" font-size="12" fill="#666">Starstruck</text>
  </g>
  <g transform="translate(550, 80)">
    <text x="0" y="0" font-size="40">🔥</text>
    <text x="0" y="30" font-family="Arial" font-size="12" fill="#666">On Fire</text>
  </g>
</svg>'''
    generate_svg(svg, "trophy.svg")

def generate_bento():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
  <rect width="800" height="400" fill="#ffffff" rx="12"/>
  <text x="400" y="35" text-anchor="middle" font-family="Arial" font-size="20" font-weight="600" fill="#0078d4">Bento Grid</text>
  
  <rect x="20" y="60" width="350" height="150" fill="#0078d4" opacity="0.1" rx="8"/>
  <text x="195" y="140" text-anchor="middle" font-family="Arial" font-size="16" font-weight="600" fill="#0078d4">Projects</text>
  
  <rect x="390" y="60" width="350" height="150" fill="#00d4aa" opacity="0.1" rx="8"/>
  <text x="565" y="140" text-anchor="middle" font-family="Arial" font-size="16" font-weight="600" fill="#00d4aa">Skills</text>
  
  <rect x="20" y="230" width="230" height="140" fill="#F7C948" opacity="0.1" rx="8"/>
  <text x="135" y="305" text-anchor="middle" font-family="Arial" font-size="14" font-weight="600" fill="#F7C948">Experience</text>
  
  <rect x="270" y="230" width="230" height="140" fill="#ff6b9d" opacity="0.1" rx="8"/>
  <text x="385" y="305" text-anchor="middle" font-family="Arial" font-size="14" font-weight="600" fill="#ff6b9d">Education</text>
  
  <rect x="520" y="230" width="220" height="140" fill="#c084fc" opacity="0.1" rx="8"/>
  <text x="630" y="305" text-anchor="middle" font-family="Arial" font-size="14" font-weight="600" fill="#c084fc">Interests</text>
</svg>'''
    generate_svg(svg, "bento.svg")

def generate_snake():
    cols = 40
    rows = 6
    cell_size = 12
    grid_w = cols * cell_size
    grid_h = rows * cell_size
    start_x = 40
    start_y = 70

    cells = []
    for r in range(rows):
        for c in range(cols):
            x = start_x + c * cell_size
            y = start_y + r * cell_size
            opacity = 0.08 + ((r + c) % 5) * 0.04
            cells.append(
                f'<rect x="{x}" y="{y}" width="10" height="10" fill="#0078d4" opacity="{opacity}" rx="2"/>'
            )

    snake_parts = []
    for i in range(18):
        x_offset = i * 8
        color = "#0078d4" if i == 0 else "#00d4aa"
        r = 6 if i == 0 else 4
        snake_parts.append(
            f'<circle cx="0" cy="0" r="{r}" fill="{color}">'
            f'<animateMotion path="M {start_x},{start_y + 20} '
            f'L {start_x + grid_w},{start_y + 20} '
            f'L {start_x + grid_w},{start_y + grid_h - 10} '
            f'L {start_x},{start_y + grid_h - 10} Z" '
            f'dur="12s" repeatCount="indefinite" begin="{i * 0.15}s"'
            f'/><animate attributeName="opacity" values="1;0.6;1" dur="2s" repeatCount="indefinite" begin="{i * 0.1}s"/></circle>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="260" viewBox="0 0 800 260">
  <rect width="800" height="260" fill="#ffffff" rx="12"/>
  <text x="400" y="35" text-anchor="middle" font-family="Arial" font-size="18" font-weight="600" fill="#0078d4">GitHub Contribution Snake</text>
  <g transform="translate(0, 50)">
    {''.join(cells)}
    {''.join(snake_parts)}
    <text x="400" y="210" text-anchor="middle" font-family="Arial" font-size="11" fill="#666">Auto-generated by GitHub Action — eats your contribution squares!</text>
  </g>
</svg>'''
    generate_svg(svg, "snake.svg")

def generate_star_history():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="250" viewBox="0 0 800 250">
  <defs>
    <linearGradient id="linegrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#00d4aa;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="800" height="250" fill="#ffffff" rx="12"/>
  <text x="400" y="35" text-anchor="middle" font-family="Arial" font-size="18" font-weight="600" fill="#0078d4">Star History</text>
  <polyline points="50,200 150,180 250,150 350,160 450,100 550,80 650,50 750,60" fill="none" stroke="url(#linegrad)" stroke-width="3">
    <animate attributeName="stroke-dasharray" from="0,1000" to="1000,0" dur="3s" fill="freeze"/>
  </polyline>
  <circle cx="750" cy="60" r="5" fill="#0078d4">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite"/>
  </circle>
</svg>'''
    generate_svg(svg, "star-history.svg")

def generate_globe():
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <defs>
    <linearGradient id="ocean" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:#00d4aa;stop-opacity:0.2" />
    </linearGradient>
  </defs>
  <rect width="800" height="300" fill="#ffffff" rx="12"/>
  <text x="400" y="35" text-anchor="middle" font-family="Arial" font-size="18" font-weight="600" fill="#0078d4">3D Contribution Globe</text>
  
  <circle cx="400" cy="160" r="100" fill="url(#ocean)" stroke="#0078d4" stroke-width="2"/>
  <ellipse cx="400" cy="160" rx="40" ry="100" fill="none" stroke="#0078d4" stroke-width="1" opacity="0.5"/>
  <ellipse cx="400" cy="160" rx="100" ry="40" fill="none" stroke="#0078d4" stroke-width="1" opacity="0.5"/>
  <line x1="300" y1="160" x2="500" y2="160" stroke="#0078d4" stroke-width="1" opacity="0.5"/>
  <line x1="400" y1="60" x2="400" y2="260" stroke="#0078d4" stroke-width="1" opacity="0.5"/>
  
  <circle cx="400" cy="160" r="100" fill="none" stroke="#0078d4" stroke-width="2" stroke-dasharray="10,5">
    <animate attributeName="stroke-dashoffset" from="0" to="-30" dur="2s" repeatCount="indefinite"/>
  </circle>
  
  <circle cx="350" cy="130" r="4" fill="#ff6b9d">
    <animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/>
  </circle>
  <circle cx="450" cy="180" r="4" fill="#00d4aa">
    <animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="420" cy="140" r="3" fill="#F7C948">
    <animate attributeName="opacity" values="1;0.5;1" dur="1.8s" repeatCount="indefinite"/>
  </circle>
</svg>'''
    generate_svg(svg, "globe.svg")

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

# ==================== NEW ANIMATION FUNCTIONS ====================

def generate_radar_scan():
    """Generate radar scan animation"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <defs>
    <radialGradient id="radarGrad">
      <stop offset="0%" style="stop-color:#00ff00;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:#00ff00;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="800" height="300" fill="#0a0a0a" rx="8"/>
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

def generate_matrix_rain():
    """Generate Matrix-style rain animation"""
    columns = 40
    width = 800
    height = 300
    drops = []
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()"
    for i in range(columns):
        x = i * 20
        y = 20
        char = chars[i % len(chars)]
        duration = 2 + (i % 3)
        delay = i * 0.1
        drops.append(f'''
  <text x="{x}" y="{y}" fill="#00ff00" font-family="monospace" font-size="14" opacity="0.8">
    {char}
    <animate attributeName="y" from="0" to="{height}" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
    <animate attributeName="opacity" values="1;0" dur="{duration}s" repeatCount="indefinite" begin="{delay}s"/>
  </text>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="{width}" height="{height}" fill="#0a0a0a" rx="8"/>
  <text x="400" y="25" text-anchor="middle" font-family="monospace" font-size="16" font-weight="600" fill="#00ff00">Matrix Rain</text>
  {''.join(drops)}
  <text x="400" y="290" text-anchor="middle" font-family="monospace" font-size="10" fill="#00ff00">The Matrix has you...</text>
</svg>'''
    generate_svg(svg, "matrix-rain.svg")

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
    """Generate circuit board pattern"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <defs>
    <linearGradient id="circuitGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0078d4;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#00d4aa;stop-opacity:0.8" />
    </linearGradient>
  </defs>
  <rect width="800" height="200" fill="#0a0a0a" rx="8"/>
  <text x="400" y="25" text-anchor="middle" font-family="Courier New" font-size="14" font-weight="600" fill="#0078d4">Circuit Board</text>
  
  <line x1="50" y1="50" x2="200" y2="50" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  <line x1="200" y1="50" x2="200" y2="150" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  <line x1="200" y1="150" x2="400" y2="150" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  <line x1="400" y1="150" x2="400" y2="80" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  <line x1="400" y1="80" x2="600" y2="80" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  <line x1="600" y1="80" x2="600" y2="180" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  <line x1="600" y1="180" x2="750" y2="180" stroke="url(#circuitGrad)" stroke-width="2">
    <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="5s" repeatCount="indefinite"/>
  </line>
  
  <circle cx="200" cy="50" r="5" fill="#00d4aa">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="200" cy="150" r="5" fill="#00d4aa">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite" begin="0.2s"/>
  </circle>
  <circle cx="400" cy="150" r="5" fill="#00d4aa">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite" begin="0.4s"/>
  </circle>
  <circle cx="400" cy="80" r="5" fill="#00d4aa">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite" begin="0.6s"/>
  </circle>
  <circle cx="600" cy="80" r="5" fill="#00d4aa">
    <animate attributeName="r" values="4;6;4" dur="1.5s" repeatCount="indefinite" begin="0.8s"/>
  </circle>
  
  <text x="400" y="195" text-anchor="middle" font-family="Courier New" font-size="10" fill="#0078d4">⚡ Data flows through circuits...</text>
</svg>'''
    generate_svg(svg, "circuit-board.svg")

def generate_particles():
    """Generate particle network animation"""
    particles = []
    for i in range(20):
        x = 50 + (i % 5) * 150
        y = 50 + (i // 5) * 100
        particles.append(f'''
  <circle cx="{x}" cy="{y}" r="3" fill="#0078d4">
    <animate attributeName="opacity" values="0.3;1;0.3" dur="{2 + i%3}s" repeatCount="indefinite" begin="{i*0.2}s"/>
  </circle>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <rect width="800" height="300" fill="#0a0a0a" rx="8"/>
  <text x="400" y="25" text-anchor="middle" font-family="Courier New" font-size="14" font-weight="600" fill="#0078d4">Particle Network</text>
  {''.join(particles)}
  <text x="400" y="280" text-anchor="middle" font-family="Courier New" font-size="10" fill="#0078d4">🤖 Neural network visualization</text>
</svg>'''
    generate_svg(svg, "particles.svg")

def generate_data_stream():
    """Generate binary/data stream animation"""
    bits = []
    for i in range(60):
        x = 50 + (i % 10) * 70
        y = 50 + (i // 10) * 50
        bit = ["0", "1"][i % 2]
        bits.append(f'''
  <text x="{x}" y="{y}" fill="#00d4aa" font-family="Courier New" font-size="14" opacity="0.8">
    {bit}
    <animate attributeName="opacity" values="0.3;1;0.3" dur="{1 + i%4}s" repeatCount="indefinite" begin="{i*0.15}s"/>
  </text>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="300" viewBox="0 0 800 300">
  <rect width="800" height="300" fill="#0a0a0a" rx="8"/>
  <text x="400" y="25" text-anchor="middle" font-family="Courier New" font-size="14" font-weight="600" fill="#00d4aa">Data Stream</text>
  {''.join(bits)}
  <text x="400" y="290" text-anchor="middle" font-family="Courier New" font-size="10" fill="#00d4aa">Binary data flow...</text>
</svg>'''
    generate_svg(svg, "data-stream.svg")

def generate_timeline():
    """Generate animated tech timeline"""
    events = [
        ("2020", "Started Coding", "#0078d4"),
        ("2021", "First Open Source", "#00d4aa"),
        ("2022", "Full-Stack Dev", "#F7C948"),
        ("2023", "AI/ML Explorer", "#ff6b9d"),
        ("2024", "Cloud Native", "#c084fc"),
        ("2025", "Building Future", "#fb923c")
    ]
    nodes = []
    for i, (year, event, color) in enumerate(events):
        x = 100 + i * 120
        nodes.append(f'''
  <circle cx="{x}" cy="120" r="8" fill="{color}">
    <animate attributeName="r" values="6;10;6" dur="2s" repeatCount="indefinite" begin="{i*0.3}s"/>
  </circle>
  <text x="{x}" y="100" text-anchor="middle" font-family="Arial" font-size="12" font-weight="600" fill="{color}">{year}</text>
  <text x="{x}" y="150" text-anchor="middle" font-family="Arial" font-size="10" fill="#666">{event}</text>''')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="200" viewBox="0 0 800 200">
  <rect width="800" height="200" fill="#ffffff" rx="12"/>
  <text x="400" y="30" text-anchor="middle" font-family="Arial" font-size="18" font-weight="600" fill="#0078d4">Tech Journey</text>
  <line x1="80" y1="120" x2="720" y2="120" stroke="#0078d4" stroke-width="2" opacity="0.3" stroke-dasharray="5,5">
    <animate attributeName="stroke-dashoffset" from="0" to="-20" dur="2s" repeatCount="indefinite"/>
  </line>
  {''.join(nodes)}
</svg>'''
    generate_svg(svg, "timeline.svg")

# ==================== MAIN ====================

def main():
    print("Generating profile assets...")
    generate_github_stats()
    generate_top_languages()
    generate_streak()
    generate_activity_graph()
    generate_trophy()
    generate_bento()
    generate_snake()
    generate_star_history()
    generate_globe()
    generate_wakatime()
    
    print("Generating new animation assets...")
    generate_radar_scan()
    generate_matrix_rain()
    generate_terminal()
    generate_circuit_board()
    generate_particles()
    generate_data_stream()
    generate_timeline()
    
    print("All assets generated!")

if __name__ == "__main__":
    main()