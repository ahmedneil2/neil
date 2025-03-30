from aiohttp import web
from database.ia_filterdb import col, sec_col

@routes.get('/health')
async def health_check(request):
    try:
        # ডাটাবেস কানেকশন চেক
        await col.find_one({})
        await sec_col.find_one({})
        
        return web.json_response({
            'status': 'healthy',
            'database': 'connected'
        })
    except Exception as e:
        return web.json_response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)

async def list_media(request):
    try:
        files = []
        
        # প্রথম ডাটাবেস থেকে ফাইল নিয়ে আসা
        cursor1 = col.find({}).sort('file_name', 1)
        async for file in cursor1:
            files.append({
                'file_id': file['file_id'],
                'file_name': file['file_name'],
                'file_size': file['file_size']
            })
            
        # দ্বিতীয় ডাটাবেস থেকে ফাইল নিয়ে আসা
        cursor2 = sec_col.find({}).sort('file_name', 1)
        async for file in cursor2:
            files.append({
                'file_id': file['file_id'],
                'file_name': file['file_name'],
                'file_size': file['file_size']
            })
            
        return web.json_response(
            {'files': files},
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        return web.json_response(
            {'error': str(e)},
            status=500,
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )

