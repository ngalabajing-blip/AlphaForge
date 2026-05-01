from __future__ import annotations

import time


def test_submit_and_inspect_audit(auth_client) -> None:
    resp = auth_client.post(
        "/api/v1/audits",
        json={"chain": "eth", "address": "0x" + "ab" * 20, "deep": False},
    )
    assert resp.status_code in (200, 201, 202), resp.text
    job_id = resp.json()["id"]

    # poll briefly
    for _ in range(10):
        out = auth_client.get(f"/api/v1/audits/{job_id}")
        if out.status_code == 200 and out.json().get("status") in ("completed", "failed"):
            assert out.json()["status"] in ("completed", "failed")
            return
        time.sleep(1.5)
