#!/usr/bin/env python3
"""
Soul Memory Web UI v1.0
FastAPI Backend + Dashboard
Author: Soul Memory System
Date: 2026-02-18
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import asdict

# FastAPI
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Add parent path for modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core import SoulMemorySystem

# Initialize FastAPI
app = FastAPI(
    title="Soul Memory Web UI",
    description="Web interface for Soul Memory System v3.0",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Global memory system instance
memory_system = None

# ============ Task System ============
class Task:
    """Background task"""
    def __init__(self, task_id: str, title: str, task_type: str):
        self.id = task_id
        self.title = title
        self.type = task_type
        self.status = "pending"  # pending | doing | done | error
        self.progress = 0
        self.start_time = None
        self.end_time = None
        self.message = ""
        self.result = None

tasks: Dict[str, Task] = {}

def create_task(title: str, task_type: str) -> Task:
    """Create new task"""
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(tasks)}"
    task = Task(task_id, title, task_type)
    tasks[task_id] = task
    return task

def update_task(task_id: str, status: str = None, progress: int = None, message: str = None):
    """Update task status"""
    if task_id in tasks:
        task = tasks[task_id]
        if status:
            task.status = status
            if status == "doing" and not task.start_time:
                task.start_time = datetime.now().isoformat()
            if status in ["done", "error"]:
                task.end_time = datetime.now().isoformat()
        if progress is not None:
            task.progress = progress
        if message:
            task.message = message

# ============ Startup ============
@app.on_event("startup")
async def startup_event():
    """Initialize memory system on startup"""
    global memory_system
    print("🧠 Initializing Soul Memory Web UI...")
    memory_system = SoulMemorySystem()
    memory_system.initialize()
    print(f"✅ Ready - {memory_system.stats()['total_segments']} segments loaded")

# ============ Pages ============
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "version": memory_system.VERSION if memory_system else "unknown"
    })

# ============ API Endpoints ============

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    stats = memory_system.stats()
    
    # Calculate priority distribution
    priority_counts = {"C": 0, "I": 0, "N": 0}
    for seg in memory_system.vector_search.segments:
        p = seg.priority
        if p in priority_counts:
            priority_counts[p] += 1
    
    return {
        "version": stats["version"],
        "total_segments": stats["total_segments"],
        "categories": stats["categories"],
        "priority_distribution": priority_counts,
        "indexed": stats["indexed"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/search")
async def search_memory(q: str, top_k: int = 10):
    """Search memory"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    results = memory_system.search(q, top_k=top_k)
    
    return {
        "query": q,
        "total": len(results),
        "results": [
            {
                "content": r.content,
                "score": r.score,
                "source": r.source,
                "line_number": r.line_number,
                "category": r.category,
                "priority": r.priority
            }
            for r in results
        ]
    }

@app.get("/api/categories")
async def get_categories():
    """Get all categories"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    # Count segments per category
    category_counts = {}
    for seg in memory_system.vector_search.segments:
        cat = seg.category or "Uncategorized"
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {
        "categories": [
            {"name": k, "count": v}
            for k, v in sorted(category_counts.items(), key=lambda x: -x[1])
        ]
    }

@app.get("/api/memory/{memory_id}")
async def get_memory(memory_id: str):
    """Get specific memory by ID"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    for seg in memory_system.vector_search.segments:
        if seg.id == memory_id:
            return {
                "id": seg.id,
                "content": seg.content,
                "source": seg.source,
                "line_number": seg.line_number,
                "category": seg.category,
                "priority": seg.priority,
                "keywords": seg.keywords
            }
    
    raise HTTPException(status_code=404, detail="Memory not found")

@app.get("/api/tasks")
async def get_tasks():
    """Get all tasks"""
    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "type": t.type,
                "status": t.status,
                "progress": t.progress,
                "start_time": t.start_time,
                "end_time": t.end_time,
                "message": t.message
            }
            for t in sorted(tasks.values(), key=lambda x: x.id, reverse=True)
        ]
    }

@app.post("/api/index/rebuild")
async def rebuild_index():
    """Trigger index rebuild"""
    if not memory_system:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    task = create_task("Rebuild Memory Index", "index")
    
    # Run in background
    asyncio.create_task(do_rebuild_index(task.id))
    
    return {"task_id": task.id, "message": "Index rebuild started"}

async def do_rebuild_index(task_id: str):
    """Background task to rebuild index"""
    update_task(task_id, status="doing", progress=0, message="Starting rebuild...")
    
    try:
        # Delete cache
        cache_file = memory_system.cache_path / "index.json"
        if cache_file.exists():
            cache_file.unlink()
        
        update_task(task_id, progress=30, message="Cleared cache")
        
        # Rebuild
        memory_system.indexed = False
        memory_system.initialize()
        
        update_task(task_id, status="done", progress=100, 
                   message=f"Rebuild complete - {memory_system.stats()['total_segments']} segments")
    except Exception as e:
        update_task(task_id, status="error", message=f"Error: {str(e)}")

class AddMemoryRequest(BaseModel):
    content: str
    category: Optional[str] = None
    priority: Optional[str] = None

