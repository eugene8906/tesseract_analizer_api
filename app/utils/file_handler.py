import os
from fastapi import UploadFile


async def save_file(file: UploadFile):
    documents_folder = 'documents'
    os.makedirs(documents_folder, exist_ok=True)

    file_path = os.path.join(documents_folder, file.filename)

    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    return file_path


def delete_file(file_path: str) -> bool:
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False