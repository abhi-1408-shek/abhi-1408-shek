import feedparser
import re
from datetime import datetime

def fetch_latest_ml_paper():
    """Fetch the latest popular ML paper from ArXiv."""
    # ArXiv API for cs.LG (Machine Learning) category, sorted by submissions
    arxiv_url = "https://export.arxiv.org/api/query?search_query=cat:cs.LG&start=0&max_results=1&sortBy=submittedDate&sortOrder=descending"
    
    feed = feedparser.parse(arxiv_url)
    
    if not feed.entries:
        return None
    
    entry = feed.entries[0]
    
    # Extract data
    title = entry.title.replace('\n', ' ').strip()
    authors = ', '.join([author.name for author in entry.authors[:3]])  # First 3 authors
    if len(entry.authors) > 3:
        authors += " et al."
    
    summary = entry.summary.replace('\n', ' ').strip()
    # Truncate summary to 300 chars
    if len(summary) > 300:
        summary = summary[:297] + "..."
    
    link = entry.link
    published = entry.published
    
    # Format as markdown
    paper_md = f"""**📄 {title}**

👥 *Authors*: {authors}

📝 *Abstract*: {summary}

🔗 [Read on ArXiv]({link})

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}*"""
    
    return paper_md

def update_readme(paper_content):
    """Update README.md with the latest paper."""
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace content between START_SECTION:arxiv and END_SECTION:arxiv
    start_marker = '<!--START_SECTION:arxiv-->'
    end_marker = '<!--END_SECTION:arxiv-->'
    
    pattern = f'{re.escape(start_marker)}.*?{re.escape(end_marker)}'
    replacement = f'{start_marker}\n{paper_content}\n{end_marker}'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ README updated with latest ML paper!")

if __name__ == "__main__":
    paper = fetch_latest_ml_paper()
    if paper:
        update_readme(paper)
    else:
        print("❌ No papers found")
