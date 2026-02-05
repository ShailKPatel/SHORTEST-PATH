from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import visualization, statistics
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Shortest Path Visualizer")

# CORS (allow all for simplicity in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include Routers
app.include_router(visualization.router)
app.include_router(statistics.router)

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/batch")
async def read_batch(request: Request):
    return templates.TemplateResponse("batch.html", {"request": request})
