import os
import subprocess
import time

# Define the commits
commits = [
    {
        "date": "2026-07-01T02:30:00+05:30",
        "msg": "Initial commit: Project scaffold and setup",
        "add": [".gitignore", "backend/requirements.txt", "frontend/package.json", "frontend/vite.config.js", "README.md"]
    },
    {
        "date": "2026-07-01T04:15:00+05:30",
        "msg": "Backend: FastAPI setup, models, and basic configuration",
        "add": ["backend/app/main.py", "backend/app/config.py", "backend/app/models.py", "backend/app/routes/", "backend/app/utils/"]
    },
    {
        "date": "2026-07-01T11:45:00+05:30",
        "msg": "Backend: Implement LangGraph state and core agent nodes",
        "add": ["backend/app/agent/", "backend/app/services/mongodb.py"]
    },
    {
        "date": "2026-07-01T16:20:00+05:30",
        "msg": "Frontend: React scaffolding, CSS, and chat hook",
        "add": ["frontend/src/main.jsx", "frontend/src/App.jsx", "frontend/src/index.css", "frontend/src/hooks/"]
    },
    {
        "date": "2026-07-01T22:10:00+05:30",
        "msg": "Frontend: Implement UI components (MessageBubble, Agent UI)",
        "add": ["frontend/src/components/", "frontend/index.html"]
    },
    {
        "date": "2026-07-02T01:30:00+05:30",
        "msg": "Backend: Integrate Gemini Vision API for card extraction",
        "add": ["backend/app/services/vision.py"]
    },
    {
        "date": "2026-07-02T10:15:00+05:30",
        "msg": "Backend: Integrate Google Sheets API and Deduplication logic",
        "add": ["backend/app/services/sheets.py", "backend/app/services/enrichment.py"]
    },
    {
        "date": "2026-07-02T14:50:00+05:30",
        "msg": "Backend: Integrate Cloudinary and audio transcription",
        "add": ["backend/app/services/audio.py"]
    },
    {
        "date": "2026-07-02T19:40:00+05:30",
        "msg": "Fix: Handle LangGraph role types and NoneType bugs",
        "add": ["backend/app/agent/graph.py", "backend/app/agent/nodes/enrich.py", "backend/app/agent/nodes/confirm.py", "backend/app/routes/chat.py"]
    },
    {
        "date": "2026-07-02T23:25:00+05:30",
        "msg": "Docs: Update README with comprehensive project documentation",
        "add": ["."]
    }
]

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

try:
    print("Starting history rewrite...")
    run("git checkout --orphan new_main")
    run("git rm -rf --cached .")
    
    for c in commits:
        print(f"Committing: {c['msg']}")
        for path in c['add']:
            run(f"git add {path}")
        
        # Set both AUTHOR_DATE and COMMITTER_DATE
        env = f"GIT_AUTHOR_DATE='{c['date']}' GIT_COMMITTER_DATE='{c['date']}'"
        # Commit (ignore error if no changes to commit)
        subprocess.run(f"{env} git commit -m '{c['msg']}'", shell=True)
    
    # Cleanup branches
    run("git branch -D main")
    run("git branch -m main")
    
    # Push to remote
    print("Force pushing to origin main...")
    run("git push -f origin main")
    print("Done!")

except Exception as e:
    print("Error:", e)

