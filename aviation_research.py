import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json
import os

# Configure your search queries and Wikipedia pages here
NEWS_QUERIES = [
    "Otto Celera 500L",
    "aviation innovation fuel efficiency",
    "new aircraft long range affordability",
    "electric aircraft",
    "hydrogen aircraft"
]

WIKIPEDIA_PAGES = [
    "Otto_Celera_500L",
    "Electric_aircraft",
    "Hydrogen-powered_aircraft"
]

def fetch_google_news(query):
    """Fetches recent news articles from Google News RSS."""
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query + ' when:7d')}&hl=en-US&gl=US&ceid=US:en"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            items = []
            for item in root.findall('./channel/item')[:5]:  # Top 5 most recent
                title = item.find('title').text
                link = item.find('link').text
                pubDate = item.find('pubDate').text
                items.append((title, link, pubDate))
            return items
    except Exception as e:
        print(f"Error fetching news for {query}: {e}")
        return []

def fetch_wiki_updates(title):
    """Fetches the latest revisions for a Wikipedia page."""
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles={urllib.parse.quote(title)}&rvprop=timestamp|comment|user&rvlimit=3&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'AviationResearchBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            pages = data['query']['pages']
            page_id = list(pages.keys())[0]
            if page_id == "-1": return []
            return pages[page_id].get('revisions', [])
    except Exception as e:
        print(f"Error fetching wiki for {title}: {e}")
        return []

def generate_report():
    date_str = datetime.now().strftime('%Y-%m-%d')
    report = f"# 🛩 Aviation Innovation Report - {date_str}\n\n"
    
    report += "## 📰 Latest News (Past 7 Days)\n\n"
    for kw in NEWS_QUERIES:
        report += f"### {kw}\n"
        news = fetch_google_news(kw)
        if not news:
            report += "*No recent news found.*\n"
        else:
            for title, link, date in news:
                report += f"- [{title}]({link}) _({date})_\n"
        report += "\n"
        
    report += "---\n\n## 📝 Wikipedia Updates (Recent Edits)\n\n"
    for page in WIKIPEDIA_PAGES:
        report += f"### [{page.replace('_', ' ')}](https://en.wikipedia.org/wiki/{page})\n"
        revs = fetch_wiki_updates(page)
        if not revs:
            report += "*No recent revisions found.*\n"
        else:
            for rev in revs:
                ts = rev.get('timestamp')
                user = rev.get('user', 'Unknown')
                comment = rev.get('comment', 'No comment provided')
                
                # Only show edits from the last 30 days
                edit_date = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                if datetime.now() - edit_date < timedelta(days=30):
                    report += f"- **{ts[:10]}** by [{user}]: _{comment}_\n"
            
            # If nothing was within 30 days
            if not any(datetime.now() - datetime.strptime(r.get('timestamp'), "%Y-%m-%dT%H:%M:%SZ") < timedelta(days=30) for r in revs):
                 report += "*No updates in the last 30 days.*\n"
        report += "\n"
    
    # Save the report
    filename = f"aviation_report_{datetime.now().strftime('%Y%m%d')}.md"
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
        
    print(f"✅ Research complete! Report generated at: {filepath}")

if __name__ == "__main__":
    generate_report()
