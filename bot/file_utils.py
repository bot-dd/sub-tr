import os
import aiofiles
import zipfile

async def extract_zip(zip_path: str, extract_to: str = "temp/") -> list:
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        return [os.path.join(extract_to, name) for name in zip_ref.namelist()]

async def read_file(file_path: str) -> str:
    async with aiofiles.open(file_path, mode='r', encoding='utf-8', errors='ignore') as f:
        return await f.read()

async def write_file(file_path: str, content: str):
    async with aiofiles.open(file_path, mode='w', encoding='utf-8') as f:
        await f.write(content)
