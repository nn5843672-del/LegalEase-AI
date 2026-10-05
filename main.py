from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

from .exporters import export_file
from .schemas import DocumentRequest, ExportRequest
from .services import generate_document

ROOT_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = ROOT_DIR / "frontend"

app = FastAPI(title="LegalEase API", version="1.0.0")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "LegalEase"}


@app.post("/api/generate")
async def generate(data: DocumentRequest):
    try:
        content, demo_mode = await generate_document(data)
        return {"content": content, "demo_mode": demo_mode}
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/export/{file_type}")
async def export_document(file_type: str, data: ExportRequest):
    if file_type not in {"txt", "docx", "pdf"}:
        raise HTTPException(status_code=404, detail="Choose txt, docx, or pdf.")
    try:
        file_bytes, media_type, filename = export_file(file_type, data.title, data.content)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not prepare the download.") from exc
    return Response(file_bytes, media_type=media_type,
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})


app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="frontend")
