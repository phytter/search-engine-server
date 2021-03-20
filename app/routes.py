from app import app
from .services.util import jsonify
from .services import search

# Public API
async def health_check(request):
    return jsonify({
        "parsed": True,
        "url": request.url,
        "query_string": request.query_string,
        "headers": list(request.headers),
        "args": request.args,
        "query_args": request.query_args,
        "form_data": request.form,
        "files": str(request.files)
    })

def add_routes(app, search_engine):
    def handler_func(*argv):
        return search.get_search(*argv, search_engine)
    #API OK
    app.add_route(health_check, '/', methods=['GET', ], name='health_check')
    app.add_route(handler_func, '/search', methods=['GET', ], name='search')


