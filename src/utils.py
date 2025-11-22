from fastapi import APIRouter
from pathlib import Path


def load_prompt(*filenames):
    base_path = Path(__file__).parent / "agents" / "prompts"
    parts = []
    for name in filenames:
        parts.append((base_path / name).read_text())
    return "\n\n".join(parts)


def group(prefix, *routers):
    group_router = APIRouter(prefix=prefix)
    for router, router_prefix, tags in routers:
        group_router.include_router(router, prefix=router_prefix, tags=tags)
    return group_router