from fastapi import HTTPException, UploadFile

READ_CHUNK_SIZE = 1024 * 1024


async def read_limited_file(file: UploadFile, max_bytes: int, too_large_detail: str) -> bytes:
    chunks = []
    total_size = 0
    while True:
        chunk = await file.read(READ_CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_bytes:
            raise HTTPException(status_code=413, detail=too_large_detail)
        chunks.append(chunk)
    return b"".join(chunks)
