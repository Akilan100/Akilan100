import os
import json
import urllib.request
import urllib.error

TOKEN = os.environ.get("GITHUB_TOKEN")
USER = os.environ.get("GITHUB_USER", "Akilan100")

GRAPHQL_QUERY = """
query {
  user(login: "%s") {
    name
    login
    avatarUrl
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        name
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalRepositoryContributions
    }
    pullRequests(states: [OPEN, MERGED, CLOSED]) {
      totalCount
    }
    issues(states: [OPEN, CLOSED]) {
      totalCount
    }
  }
}
""" % USER

def fetch_data():
    headers = {
        "User-Agent": "Akilan-Cyber-Telemetry-Engine",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": GRAPHQL_QUERY}).encode("utf-8"),
        headers=headers
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        data = json.loads(res.read().decode("utf-8"))
        return data["data"]["user"]

def generate_stats_svg(user_data):
    repos = user_data["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)
    total_forks = sum(r["forkCount"] for r in repos)
    total_commits = user_data["contributionsCollection"]["totalCommitContributions"]
    total_prs = user_data["pullRequests"]["totalCount"]
    total_issues = user_data["issues"]["totalCount"]
    total_repos = user_data["repositories"]["totalCount"]

    svg = f"""<svg width="480" height="225" viewBox="0 0 480 225" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="neon_border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00FF66" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#00B4D8" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#00FF66" stop-opacity="0.9"/>
    </linearGradient>
  </defs>
  <style>
    .terminal-bg {{ fill: #0a0e14; stroke: url(#neon_border); stroke-width: 1.5; }}
    .title-bar {{ fill: #121820; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .term-title {{ font: 600 11px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #6e7681; }}
    .header {{ font: 700 14px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #00FF66; }}
    .stat-label {{ font: 500 12.5px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #8b949e; }}
    .stat-value {{ font: 700 13px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #00FF66; }}
    .rank-circle {{ stroke: #00FF66; stroke-width: 3.5; fill: none; }}
    .rank-text {{ font: 800 26px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #00FF66; text-anchor: middle; dominant-baseline: central; }}
    .rank-sub {{ font: 600 10px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #58a6ff; text-anchor: middle; letter-spacing: 1px; }}
  </style>

  <!-- Frame & Window Base -->
  <rect width="478" height="223" x="1" y="1" rx="8" class="terminal-bg"/>
  <path d="M1 9C1 4.58172 4.58172 1 9 1H471C475.418 1 479 4.58172 479 9V28H1V9Z" class="title-bar"/>
  <line x1="1" y1="28" x2="479" y2="28" stroke="#1f2937" stroke-width="1"/>

  <!-- Terminal Window Controls -->
  <circle cx="16" cy="14" r="5" class="dot-red"/>
  <circle cx="32" cy="14" r="5" class="dot-yellow"/>
  <circle cx="48" cy="14" r="5" class="dot-green"/>
  <text x="70" y="18" class="term-title">secops@elliot: /sys/telemetry/stats</text>

  <!-- Section Header -->
  <g transform="translate(24, 52)">
    <text class="header" x="0" y="0">&gt; EXEC_STATUS: 0x00 [TELEMETRY_ONLINE]</text>
  </g>

  <!-- Stats Grid -->
  <g transform="translate(24, 80)">
    <!-- Stars -->
    <g transform="translate(0, 0)">
      <text class="stat-label" x="0" y="0">[+] Stars Earned      :</text>
      <text class="stat-value" x="195" y="0">{total_stars:02d}</text>
    </g>
    <!-- Repositories -->
    <g transform="translate(0, 24)">
      <text class="stat-label" x="0" y="0">[+] Total Repositories :</text>
      <text class="stat-value" x="195" y="0">{total_repos:02d}</text>
    </g>
    <!-- PRs & Issues -->
    <g transform="translate(0, 48)">
      <text class="stat-label" x="0" y="0">[+] PRs &amp; Sec Issues  :</text>
      <text class="stat-value" x="195" y="0">{total_prs + total_issues:02d}</text>
    </g>
    <!-- Commits -->
    <g transform="translate(0, 72)">
      <text class="stat-label" x="0" y="0">[+] Total Commits YTD  :</text>
      <text class="stat-value" x="195" y="0">{total_commits:02d}</text>
    </g>
    <!-- System Security Status -->
    <g transform="translate(0, 96)">
      <text class="stat-label" x="0" y="0">[+] Sec Clearance      :</text>
      <text class="stat-value" x="195" y="0" fill="#58a6ff">LEVEL_4_ROOT</text>
    </g>
  </g>

  <!-- Right Rank HUD -->
  <g transform="translate(395, 126)">
    <circle cx="0" cy="0" r="44" class="rank-circle" stroke-dasharray="276" stroke-dashoffset="35"/>
    <text class="rank-text" x="0" y="-3">A+</text>
    <text class="rank-sub" x="0" y="18">CYBER_OP</text>
  </g>
</svg>"""
    return svg

def generate_langs_svg(user_data):
    lang_sizes = {}
    lang_colors = {}
    for repo in user_data["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            color = edge["node"]["color"] or "#8b949e"
            size = edge["size"]
            lang_sizes[name] = lang_sizes.get(name, 0) + size
            lang_colors[name] = color

    total_size = sum(lang_sizes.values())
    if total_size == 0:
        total_size = 1

    sorted_langs = sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Progress segments
    progress_bars = []
    curr_x = 24
    bar_width = 430
    for name, size in sorted_langs:
        pct = (size / total_size)
        w = round(pct * bar_width, 1)
        if w > 0:
            progress_bars.append((name, lang_colors.get(name, "#00FF66"), curr_x, w, pct * 100))
            curr_x += w

    # Legend items
    legend_items = []
    for i, (name, color, _, _, pct) in enumerate(progress_bars):
        col = i % 2
        row = i // 2
        x = 24 + col * 220
        y = 104 + row * 26
        legend_items.append(f"""
    <g transform="translate({x}, {y})">
      <rect x="0" y="2" width="10" height="10" rx="2" fill="{color}"/>
      <text class="stat-name" x="18" y="11">{name}</text>
      <text class="stat-pct" x="145" y="11">{pct:.1f}%</text>
    </g>""")

    svg_bars = "\n".join([f'<rect x="{x}" y="64" width="{w}" height="12" fill="{color}" rx="2"/>' for _, color, x, w, _ in progress_bars])
    svg_legend = "\n".join(legend_items)

    svg = f"""<svg width="480" height="225" viewBox="0 0 480 225" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="neon_border_langs" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00FF66" stop-opacity="0.9"/>
      <stop offset="50%" stop-color="#00B4D8" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#00FF66" stop-opacity="0.9"/>
    </linearGradient>
  </defs>
  <style>
    .terminal-bg {{ fill: #0a0e14; stroke: url(#neon_border_langs); stroke-width: 1.5; }}
    .title-bar {{ fill: #121820; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .term-title {{ font: 600 11px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #6e7681; }}
    .header {{ font: 700 14px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #00FF66; }}
    .stat-name {{ font: 600 12.5px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #e6edf3; }}
    .stat-pct {{ font: 700 12.5px 'Fira Code', 'JetBrains Mono', Consolas, monospace; fill: #00FF66; }}
    .progress-track {{ fill: #161b22; stroke: #30363d; stroke-width: 1; }}
  </style>

  <!-- Frame & Window Base -->
  <rect width="478" height="223" x="1" y="1" rx="8" class="terminal-bg"/>
  <path d="M1 9C1 4.58172 4.58172 1 9 1H471C475.418 1 479 4.58172 479 9V28H1V9Z" class="title-bar"/>
  <line x1="1" y1="28" x2="479" y2="28" stroke="#1f2937" stroke-width="1"/>

  <!-- Terminal Controls -->
  <circle cx="16" cy="14" r="5" class="dot-red"/>
  <circle cx="32" cy="14" r="5" class="dot-yellow"/>
  <circle cx="48" cy="14" r="5" class="dot-green"/>
  <text x="70" y="18" class="term-title">secops@elliot: /sys/telemetry/languages</text>

  <!-- Section Header -->
  <g transform="translate(24, 52)">
    <text class="header" x="0" y="0">&gt; MEMORY_ALLOC: LANGUAGE_WEIGHTS</text>
  </g>

  <!-- Progress Bar Track & Segments -->
  <rect x="24" y="64" width="430" height="12" rx="6" class="progress-track"/>
  {svg_bars}

  <!-- Legend -->
  {svg_legend}
</svg>"""
    return svg

if __name__ == "__main__":
    os.makedirs("dist", exist_ok=True)
    user_data = fetch_data()
    
    stats_svg = generate_stats_svg(user_data)
    with open("dist/github-stats.svg", "w", encoding="utf-8") as f:
        f.write(stats_svg)

    langs_svg = generate_langs_svg(user_data)
    with open("dist/top-langs.svg", "w", encoding="utf-8") as f:
        f.write(langs_svg)

    print("Successfully generated cyber terminal SVG telemetry cards.")
