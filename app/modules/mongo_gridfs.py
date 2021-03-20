import traceback
from app import app
from bson import ObjectId

#https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_gridfs.html
async def gridfs_upload(fileData,filename,contentType):
    try:
        from motor.motor_asyncio import (AsyncIOMotorGridFSBucket)
        lazy_instance = app.config.get('LAZY_UMONGO', None)
        if lazy_instance is not None:
            database = lazy_instance.db
            fs = AsyncIOMotorGridFSBucket(database)
            file_id = await fs.upload_from_stream(
                filename,
                fileData,
                chunk_size_bytes=16770000,
                metadata={"contentType": contentType})
            # print(file_id)
            return file_id
    except:
        traceback.print_exc()
        raise Exception("Erro com gridfs")
    return None

#https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_gridfs.html
async def gridfs_download(gridfsId):
    try:
        from motor.motor_asyncio import (AsyncIOMotorGridFSBucket)
        lazy_instance = app.config.get('LAZY_UMONGO', None)
        if lazy_instance is not None:
            database = lazy_instance.db
            fs = AsyncIOMotorGridFSBucket(database)
            grid_out = await fs.open_download_stream(ObjectId(gridfsId))
            contents = await grid_out.read()
            return contents
    except:
        traceback.print_exc()
        raise Exception("Erro download gridfs")
    return None


#https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_gridfs.html
async def gridfs_delete(gridfsId):
    try:
        from motor.motor_asyncio import (AsyncIOMotorGridFSBucket)
        lazy_instance = app.config.get('LAZY_UMONGO', None)
        if lazy_instance is not None:
            database = lazy_instance.db
            fs = AsyncIOMotorGridFSBucket(database)
            await fs.delete(ObjectId(gridfsId))
            return True
    except:
        traceback.print_exc()
        raise Exception("Erro download gridfs")
    return False