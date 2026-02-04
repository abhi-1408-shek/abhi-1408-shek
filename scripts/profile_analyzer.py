"""
GitHub Profile Analyzer
=======================
Generates unique, personalized profile sections:
1. Currently Thinking About (from recent commits)
2. Repo Spotlight (weekly rotating feature)
3. Commit Personality (analysis of commit patterns)
4. GitHub Timeline (milestones in your coding journey)
"""

import os
import re
import json
import requests
from datetime import datetime, timedelta
from collections import Counter
import random

USERNAME = "abhi-1408-shek"
GITHUB_API = f"https://api.github.com/users/{USERNAME}"

def get_recent_commits():
    """Fetch recent commits across all repos."""
    repos_url = f"{GITHUB_API}/repos?sort=pushed&per_page=5"
    repos = requests.get(repos_url).json()
    
    commits = []
    for repo in repos[:5]:
        if isinstance(repo, dict) and 'name' in repo:
            commits_url = f"https://api.github.com/repos/{USERNAME}/{repo['name']}/commits?per_page=10"
            repo_commits = requests.get(commits_url).json()
            if isinstance(repo_commits, list):
                for c in repo_commits[:5]:
                    if isinstance(c, dict) and 'commit' in c:
                        commits.append({
                            'message': c['commit']['message'].split('\n')[0],
                            'repo': repo['name'],
                            'date': c['commit']['author']['date']
                        })
    return commits

def generate_thinking_about(commits):
    """Generate 'Currently Thinking About' from recent commits."""
    if not commits:
        return "Exploring new technologies..."
    
    # Extract keywords from commit messages
    keywords = []
    tech_terms = ['ml', 'ai', 'react', 'python', 'java', 'api', 'database', 'ui', 'ux', 
                  'model', 'train', 'neural', 'data', 'algorithm', 'optimize', 'feature',
                  'bug', 'fix', 'update', 'refactor', 'add', 'implement', 'rag', 'vector']
    
    for c in commits[:10]:
        words = c['message'].lower().split()
        for word in words:
            if len(word) > 3 and word in tech_terms:
                keywords.append(word.capitalize())
    
    if keywords:
        top_keywords = Counter(keywords).most_common(3)
        topics = [k[0] for k in top_keywords]
        return f"Exploring: {', '.join(topics)}"
    
    # Fallback to repo names
    repos = list(set([c['repo'] for c in commits[:5]]))
    return f"Working on: {', '.join(repos[:3])}"

def generate_repo_spotlight():
    """Generate weekly rotating repo spotlight."""
    repos_url = f"{GITHUB_API}/repos?sort=updated&per_page=10"
    repos = requests.get(repos_url).json()
    
    # Filter out profile repo and empty repos
    valid_repos = [r for r in repos if isinstance(r, dict) 
                   and r.get('name') != USERNAME 
                   and r.get('description')]
    
    if not valid_repos:
        valid_repos = [r for r in repos if isinstance(r, dict) and r.get('name') != USERNAME]
    
    if not valid_repos:
        return None
    
    # Use week number to rotate
    week_num = datetime.now().isocalendar()[1]
    selected = valid_repos[week_num % len(valid_repos)]
    
    return {
        'name': selected.get('name', 'Unknown'),
        'description': selected.get('description') or 'A cool project',
        'language': selected.get('language') or 'Multiple',
        'stars': selected.get('stargazers_count', 0),
        'url': selected.get('html_url', '#')
    }

def generate_commit_personality(commits):
    """Analyze commit patterns for 'Commit Personality'."""
    if not commits:
        return {}
    
    # Analyze commit times
    hours = []
    days = []
    words = []
    
    for c in commits:
        try:
            dt = datetime.fromisoformat(c['date'].replace('Z', '+00:00'))
            hours.append(dt.hour)
            days.append(dt.strftime('%A'))
        except:
            pass
        
        # Common words in messages
        msg_words = c['message'].lower().split()
        words.extend([w for w in msg_words if len(w) > 3])
    
    personality = {}
    
    # Most active hour
    if hours:
        most_common_hour = Counter(hours).most_common(1)[0][0]
        if most_common_hour < 6:
            personality['time_emoji'] = '🌙'
            personality['time_desc'] = 'Night Owl'
        elif most_common_hour < 12:
            personality['time_emoji'] = '🌅'
            personality['time_desc'] = 'Early Bird'
        elif most_common_hour < 18:
            personality['time_emoji'] = '☀️'
            personality['time_desc'] = 'Day Coder'
        else:
            personality['time_emoji'] = '🌆'
            personality['time_desc'] = 'Evening Hacker'
    
    # Most active day
    if days:
        fav_day = Counter(days).most_common(1)[0][0]
        personality['fav_day'] = fav_day
    
    # Favorite word
    if words:
        # Filter common words
        stop_words = ['the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'added', 'update']
        filtered = [w for w in words if w not in stop_words]
        if filtered:
            personality['fav_word'] = Counter(filtered).most_common(1)[0][0]
    
    return personality

def generate_timeline():
    """Generate GitHub journey timeline."""
    # Get user creation date
    user_data = requests.get(GITHUB_API).json()
    created_at = user_data.get('created_at', '')
    
    # Get oldest repos
    repos_url = f"{GITHUB_API}/repos?sort=created&direction=asc&per_page=5"
    repos = requests.get(repos_url).json()
    
    timeline = []
    
    if created_at:
        try:
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            timeline.append({
                'date': dt.strftime('%b %Y'),
                'event': '🎉 Joined GitHub',
                'icon': '🚀'
            })
        except:
            pass
    
    # First repo
    if repos and isinstance(repos, list) and len(repos) > 0:
        first_repo = repos[0]
        if isinstance(first_repo, dict):
            try:
                dt = datetime.fromisoformat(first_repo.get('created_at', '').replace('Z', '+00:00'))
                timeline.append({
                    'date': dt.strftime('%b %Y'),
                    'event': f"📁 First Repo: {first_repo.get('name', 'Unknown')}",
                    'icon': '💻'
                })
            except:
                pass
    
    # Add current year
    timeline.append({
        'date': datetime.now().strftime('%b %Y'),
        'event': '🔥 Still Going Strong!',
        'icon': '⚡'
    })
    
    return timeline

def update_readme(thinking, spotlight, personality, timeline):
    """Update README with all generated sections."""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    now = datetime.now().strftime('%Y-%m-%d')
    
    # Build the unique sections
    sections = f"""<!--START_SECTION:unique-->
## 🧠 Currently Thinking About
> {thinking}

## 🌟 Repo Spotlight (This Week)
"""
    
    if spotlight:
        sections += f"""
| | |
|---|---|
| **[{spotlight['name']}]({spotlight['url']})** | {spotlight['description']} |
| 🔤 {spotlight['language']} | ⭐ {spotlight['stars']} stars |
"""
    
    sections += "\n## 🎭 My Commit Personality\n"
    
    if personality:
        sections += f"""| Trait | Value |
|-------|-------|
| ⏰ Coding Style | {personality.get('time_emoji', '💻')} {personality.get('time_desc', 'Consistent')} |
| 📅 Most Active | {personality.get('fav_day', 'Every day')} |
| 💬 Favorite Word | `{personality.get('fav_word', 'code')}` |
"""
    
    sections += "\n## 📅 My GitHub Journey\n"
    sections += "| When | Milestone |\n|------|----------|\n"
    for item in timeline:
        sections += f"| {item['icon']} {item['date']} | {item['event']} |\n"
    
    sections += f"\n*Auto-updated: {now}*\n<!--END_SECTION:unique-->"
    
    # Replace or append
    pattern = r'<!--START_SECTION:unique-->.*?<!--END_SECTION:unique-->'
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, sections, content, flags=re.DOTALL)
    else:
        # Insert before tech stack section
        insert_marker = '<h2 align="center">🛠️ Tech Stack</h2>'
        if insert_marker in content:
            content = content.replace(insert_marker, sections + "\n\n" + insert_marker)
        else:
            content += "\n\n" + sections
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ README updated with unique sections!")

if __name__ == "__main__":
    print("📊 Fetching your GitHub data...")
    commits = get_recent_commits()
    
    print("🧠 Generating 'Currently Thinking About'...")
    thinking = generate_thinking_about(commits)
    
    print("🌟 Selecting 'Repo Spotlight'...")
    spotlight = generate_repo_spotlight()
    
    print("🎭 Analyzing 'Commit Personality'...")
    personality = generate_commit_personality(commits)
    
    print("📅 Building 'GitHub Timeline'...")
    timeline = generate_timeline()
    
    print("📝 Updating README...")
    update_readme(thinking, spotlight, personality, timeline)
    
    print("\n🎉 Done! Your profile is now ultra-unique!")
