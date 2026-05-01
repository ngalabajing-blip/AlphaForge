"""Top-level audit orchestrator."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx

from alphaforge_auditor.fetchers.bytecode import BytecodeFetcher
from alphaforge_auditor.fetchers.source import SourceFetcher
from alphaforge_auditor.scanners.bytecode_scanner import BytecodeScanner
from alphaforge_auditor.scanners.source_scanner import SourceScanner
from alphaforge_auditor.scanners.token_scanner import TokenScanner
from alphaforge_auditor.scoring import score_findings
from alphaforge_shared.logging import get_logger

log = get_logger("alphaforge_auditor.engine")


class AuditEngine:
    async def run_audit(self, request: dict[str, Any]) -> dict[str, Any]:
        chain = str(request.get("chain", "eth")).lower()
        address = str(request.get("address", "")).lower()
        deep = bool(request.get("deep", False))
        job_id = request.get("job_id")
        log.info("audit_start", chain=chain, address=address, deep=deep, job_id=job_id)

        async with httpx.AsyncClient(timeout=30.0) as http:
            bytecode_fetcher = BytecodeFetcher(http)
            source_fetcher = SourceFetcher(http)
            bytecode = await bytecode_fetcher.fetch(chain, address)
            source = await source_fetcher.fetch(chain, address) if deep else None

        findings: list[dict[str, Any]] = []
        if bytecode is None:
            return {
                "job_id": job_id,
                "chain": chain,
                "address": address,
                "status": "failed",
                "error": "bytecode_unavailable",
                "completed_at": datetime.now(tz=timezone.utc).isoformat(),
            }

        bytecode_scanner = BytecodeScanner()
        findings.extend(bytecode_scanner.analyse(bytecode))

        if source and source.get("source_code"):
            source_scanner = SourceScanner()
            findings.extend(source_scanner.analyse(source["source_code"]))

        token_scanner = TokenScanner()
        findings.extend(await token_scanner.analyse(chain, address))

        scored = score_findings(findings)
        return {
            "job_id": job_id,
            "chain": chain,
            "address": address,
            "status": "completed",
            "risk_score": scored.risk_score,
            "risk_level": scored.risk_level,
            "summary": scored.summary,
            "findings": findings,
            "bytecode_size": len(bytecode),
            "has_source": bool(source and source.get("source_code")),
            "completed_at": datetime.now(tz=timezone.utc).isoformat(),
        }
