import httpx
from config import SUPABASE_URL, SUPABASE_SECRET_KEY


def public_url(bucket: str, path: str) -> str:
    return f"{SUPABASE_URL}/storage/v1/object/public/{bucket}/{path}"


def upload(bucket: str, path: str, data: bytes, content_type: str) -> None:
    r = httpx.post(
        f"{SUPABASE_URL}/storage/v1/object/{bucket}/{path}",
        headers={"apikey": SUPABASE_SECRET_KEY, "Content-Type": content_type},
        content=data,
        timeout=120,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"Storage upload fail: {r.status_code} {r.text}")