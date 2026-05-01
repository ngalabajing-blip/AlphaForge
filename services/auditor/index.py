"""AlphaForge Auditor — Vercel serverless."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

app = FastAPI(title="AlphaForge Auditor", version="0.1.0", default_response_class=ORJSONResponse)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_DANGEROUS_OPCODES = {"SELFDESTRUCT": "selfdestruct detected", "DELEGATECALL": "delegatecall detected", "CALLCODE": "callcode detected"}
_HONEYPOT_PATTERNS = ["blacklist", "whitelist", "isBlacklisted", "maxTxAmount", "hiddenMint"]

@app.get("/")
async def root():
    return {"service": "auditor", "status": "running", "capabilities": ["bytecode_scan", "source_scan"]}

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/v1/auditor/scan/bytecode")
async def scan_bytecode(body: dict):
    bytecode = body.get("bytecode", "0x").lower()
    findings = []
    if "ff" in bytecode[2:] and len(bytecode) > 4:
        findings.append({"severity": "critical", "type": "selfdestruct", "description": "SELFDESTRUCT opcode detected"})
    if "f4" in bytecode[2:]:
        findings.append({"severity": "high", "type": "delegatecall", "description": "DELEGATECALL opcode detected"})
    if len(bytecode) > 50000:
        findings.append({"severity": "medium", "type": "oversized", "description": f"Bytecode unusually large ({len(bytecode)} chars)"})
    return {"findings": findings, "count": len(findings)}

@app.post("/api/v1/auditor/scan/source")
async def scan_source(body: dict):
    source = body.get("source_code", "").lower()
    findings = []
    for pattern in _HONEYPOT_PATTERNS:
        if pattern in source:
            findings.append({"severity": "high", "type": "suspicious_pattern", "description": f"Found '{pattern}' in source"})
    if "selfdestruct" in source:
        findings.append({"severity": "critical", "type": "selfdestruct", "description": "selfdestruct in source code"})
    if "tx.origin" in source:
        findings.append({"severity": "medium", "type": "tx_origin", "description": "tx.origin usage detected"})
    return {"findings": findings, "count": len(findings)}
