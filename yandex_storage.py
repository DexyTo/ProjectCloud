import boto3

from config import config

def get_yandex_storage_client():
    return boto3.client(
        's3',
        endpoint_url=config.YC_ENDPOINT_URL,
        aws_access_key_id=config.YC_ACCESS_KEY,
        aws_secret_access_key=config.YC_SECRET_KEY
    )

def upload_to_yandex_cloud(file, filename):
    try:
        s3 = get_yandex_storage_client()
        
        s3.upload_fileobj(
            file,
            config.YC_BUCKET_NAME,
            filename
        )
        return True
    except Exception as e:
        print(f"Ошибка загрузки в бакет: {e}")
        return False

def delete_from_yandex_cloud(filename):
    try:
        s3 = get_yandex_storage_client()
        
        s3.delete_object(Bucket=config.YC_BUCKET_NAME, Key=filename)
        return True
    except Exception as e:
        print(f"Ошибка удаления файла из бакета: {e}")
        return False