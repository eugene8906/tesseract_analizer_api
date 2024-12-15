

async def test_upload_document(ac, test_file_path):
    with open(test_file_path, 'rb') as file:
        response = await ac.post(
            '/upload_doc',
            files={'file': ('text1.png', file, 'image/png')}
        )
    assert response.status_code == 200
