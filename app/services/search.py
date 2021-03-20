from app import app
import traceback
from .util import jsonify
import time

async def get_search(request, search_engine):
    init = time.time()
    # PAGINACAO
    page_size = 10
    page_num = 1

    query = {}
    search = ''
    filter = {}
    for key, value in request.args.items():
        try:
            if key == 'page_size':
                page_size = int(value[0])
            elif key == 'page_num':
                page_num = int(value[0])
            elif key == 'sort':
                sort = value[0]
            elif key == 'text':
                search = value[0]
            else:
                query[key] = value[0]
        except:
            return jsonify(body={"erro": traceback.format_exc()}, status=400)

    results = search_engine.search_ranked(search)
    total = len(results)
    # Calculate number of documents to skip
    skips = page_size * (page_num - 1)
        
    results = results[skips:skips + page_size]
    end = time.time()
    return jsonify({'docs': results, 'total': total, 'page_size': page_size, 'page_num': page_num, 'time_elapsed': end - init})
