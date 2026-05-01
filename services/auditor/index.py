"""Vercel serverless entrypoint for AlphaForge Auditor service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Auditor", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"service": "auditor", "status": "running (serverless mode)", "capabilities": ["bytecode_scan", "source_scan"]}


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/api/v1/auditor/scan/bytecode")
async def scan_bytecode(body: dict):
    """Scan EVM bytecode for dangerous patterns."""
    from alphaforge_auditor.scanners.bytecode_scanner import BytecodeScanner
    bytecode = body.get("bytecode", "0x")
    scanner = BytecodeScanner()
    findings = scanner.analyse(bytecode)
    return {"findings": findings, "count": len(findings)}


@app.post("/api/v1/auditor/scan/source")
async def scan_source(body: dict):
    """Scan Solidity source for dangerous patterns."""
    from alphaforge_auditor.scanners.source_scanner import SourceScanner
    source_code = body.get("source_code", "")
    scanner = SourceScanner()
    findings = scanner.analyse(source_code)
    return {"findings": findings, "count": len(findings)}


@app.post("/api/v1/auditor/audit")
async def run_audit(body: dict):
    """Run full audit (fetches from blockchain explorers)."""
    from alphaforge_auditor.engine import AuditEngine
    engine = AuditEngine()
    result = await engine.run_audit(body)
    return result
