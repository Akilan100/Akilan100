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
        "User-Agent": "Akilan-Profile-Generator",
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

    svg = f"""<svg width="450" height="195" viewBox="0 0 450 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 17px 'Segoe UI', Ubuntu, Sans-Serif; fill: #00FF66; }}
    .stat-label {{ font: 400 13px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
    .stat-value {{ font: 600 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: #e6edf3; }}
    .rank-circle {{ stroke: #00FF66; stroke-width: 4; fill: none; }}
    .rank-text {{ font: 700 24px 'Segoe UI', Ubuntu, Sans-Serif; fill: #00FF66; text-anchor: middle; dominant-baseline: central; }}
    .rank-sub {{ font: 500 10px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; text-anchor: middle; }}
  </style>
  <rect width="448" height="193" x="1" y="1" rx="8" fill="#0d1117" stroke="#00FF66" stroke-width="1.5"/>
  
  <!-- Header -->
  <g transform="translate(25, 32)">
    <text class="header" x="0" y="0">⚡ Akilan's GitHub Telemetry</text>
  </g>

  <!-- Left Stats Column -->
  <g transform="translate(25, 60)">
    <g transform="translate(0, 0)">
      <circle cx="5" cy="5" r="3" fill="#00FF66"/>
      <text class="stat-label" x="16" y="9">Total Stars Earned:</text>
      <text class="stat-value" x="160" y="9">{total_stars}</text>
    </g>
    <g transform="translate(0, 26)">
      <circle cx="5" cy="5" r="3" fill="#00FF66"/>
      <text class="stat-label" x="16" y="9">Total Repositories:</text>
      <text class="stat-value" x="160" y="9">{total_repos}</text>
    </g>
    <g transform="translate(0, 52)">
      <circle cx="5" cy="5" r="3" fill="#00FF66"/>
      <text class="stat-label" x="16" y="9">Total PRs &amp; Issues:</text>
      <text class="stat-value" x="160" y="9">{total_prs + total_issues}</text>
    </g>
    <g transform="translate(0, 78)">
      <circle cx="5" cy="5" r="3" fill="#00FF66"/>
      <text class="stat-label" x="16" y="9">Total Commits (YTD):</text>
      <text class="stat-value" x="160" y="9">{total_commits}</text>
    </g>
  </g>

  <!-- Right Rank Badge -->
  <g transform="translate(355, 105)">
    <circle cx="0" cy="0" r="42" class="rank-circle" stroke-dasharray="260" stroke-dashoffset="30"/>
    <text class="rank-text" x="0" y="-3">A+</text>
    <text class="rank-sub" x="0" y="16">OPERATOR</text>
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
    
    # Calculate progress segments
    progress_bars = []
    curr_x = 25
    bar_width = 400
    for name, size in sorted_langs:
        pct = (size / total_size)
        w = round(pct * bar_width, 1)
        if w > 0:
            progress_bars.append((name, lang_colors.get(name, "#00FF66"), curr_x, w, pct * 100))
            curr_x += w

    # Legend items (2 rows)
    legend_items = []
    for i, (name, color, _, _, pct) in enumerate(progress_bars):
        col = i % 2
        row = i // 2
        x = 25 + col * 200
        y = 100 + row * 26
        legend_items.append(f"""
    <g transform="translate({x}, {y})">
      <circle cx="6" cy="6" r="5" fill="{color}"/>
      <text class="stat-value" x="18" y="10">{name}</text>
      <text class="stat-label" x="130" y="10">{pct:.1f}%</text>
    </g>""")

    svg_bars = "\n".join([f'<rect x="{x}" y="60" width="{w}" height="10" fill="{color}" rx="2"/>' for _, color, x, w, _ in progress_bars])
    svg_legend = "\n".join(legend_items)

    svg = f"""<svg width="450" height="195" viewBox="0 0 450 195" fill="none" xmlns="http://www.w3.org/2000/svg">
  <style>
    .header {{ font: 600 17px 'Segoe UI', Ubuntu, Sans-Serif; fill: #00FF66; }}
    .stat-label {{ font: 400 13px 'Segoe UI', Ubuntu, Sans-Serif; fill: #8b949e; }}
    .stat-value {{ font: 600 13px 'Segoe UI', Ubuntu, Sans-Serif; fill: #e6edf3; }}
  </style>
  <rect width="448" height="193" x="1" y="1" rx="8" fill="#0d1117" stroke="#00FF66" stroke-width="1.5"/>
  
  <!-- Header -->
  <g transform="translate(25, 32)">
    <text class="header" x="0" y="0">🛠️ Most Used Languages</text>
  </g>

  <!-- Progress Bar Base & Segments -->
  <rect x="25" y="60" width="400" height="10" rx="5" fill="#21262d"/>
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

    print("Successfully generated dist/github-stats.svg and dist/top-langs.svg")
