def page_of(rows: list, page: int, page_size: int) -> dict:
    safe_page = max(page, 1)
    safe_size = min(max(page_size, 1), 100)
    start = (safe_page - 1) * safe_size
    return {"page": safe_page, "page_size": safe_size, "total": len(rows), "rows": rows[start:start + safe_size]}
