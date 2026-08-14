from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import require_admin
from ..schemas.audit import (
    BulkAutoResult, BulkManualRequest, BulkManualResult, FixAllFlaggedResult,
    FlaggedItem, FullCleanupStartResponse, FullCleanupStatusResponse,
    IgnoreRemainingResult, MessageResponse, ScanResponse, StructuralFixResult,
)
from ..services import audit_service

router = APIRouter(
    prefix="/api/audit", tags=["audit"],
    dependencies=[Depends(require_admin)],
)


@router.get("/scan", response_model=ScanResponse)
def get_scan(force: bool = False):
    return audit_service.get_scan(force=force)


@router.post("/structural-fix", response_model=StructuralFixResult)
def structural_fix():
    res = audit_service.auto_fix_structural()
    audit_service.force_rescan()
    return res


@router.post("/full-cleanup", response_model=FullCleanupStartResponse)
def full_cleanup():
    job_id = audit_service.start_full_cleanup()
    return {"job_id": job_id}


@router.get("/full-cleanup/{job_id}", response_model=FullCleanupStatusResponse)
def full_cleanup_status(job_id: str):
    return audit_service.get_job_status(job_id)


@router.post("/bulk-auto", response_model=BulkAutoResult)
def bulk_auto():
    res = audit_service.bulk_auto()
    audit_service.force_rescan()
    return res


@router.post("/bulk-manual", response_model=BulkManualResult)
def bulk_manual(req: BulkManualRequest):
    res = audit_service.bulk_manual([it.model_dump() for it in req.items])
    if res["done"] > 0:
        audit_service.force_rescan()
    return res


@router.post("/ignore-remaining", response_model=IgnoreRemainingResult)
def ignore_remaining():
    scan = audit_service.get_scan()
    unknown = [
        b["token"] for b in scan["bare_words"]
        if b["recommend_action"] is None and not b["is_geometry_label"]
    ]
    n = audit_service.ignore_tokens_bulk(unknown)
    audit_service.force_rescan()
    return {"ignored": n}


@router.post("/save-baseline", response_model=MessageResponse)
def save_baseline():
    audit_service.save_baseline()
    audit_service.force_rescan()
    return {"ok": True}


@router.get("/flagged", response_model=list[FlaggedItem])
def get_flagged():
    return audit_service.list_flagged()


@router.post("/flagged/{flag_id}/fix", response_model=MessageResponse)
def fix_flagged(flag_id: int):
    audit_service.fix_flagged_one(flag_id)
    return {"ok": True}


@router.post("/flagged/{flag_id}/resolve", response_model=MessageResponse)
def resolve_flagged(flag_id: int):
    audit_service.resolve_flagged(flag_id)
    return {"ok": True}


@router.post("/flagged/fix-all", response_model=FixAllFlaggedResult)
def fix_all_flagged():
    return audit_service.fix_all_flagged()
