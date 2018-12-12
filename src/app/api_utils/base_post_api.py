import consts

from flask_restful import Resource

from app.application import cache
from . import thumbnails, postmeta, html_utils


class BasePostApi(Resource):
    def get(self):
        return self._build_data_list()

    def _build_data_list(self):
        raise NotImplementedError

    def _query_posts(self):
        raise NotImplementedError

    def _build_post(self, parent, revision):
        parent_id = getattr(parent, 'id', '')
        if parent_id:
            data = revision or parent
            auction_start = postmeta.by_key(parent.id, 'aukcja_start', None)
            auction_end = postmeta.by_key(parent.id, 'aukcja_end', None)

            if auction_start and auction_end:
                return {
                    'id': parent_id,
                    'title': html_utils.clean(getattr(data, 'post_title', '')),
                    'description_content': html_utils.clean(getattr(data, 'post_content', '')),
                    'description_excerpt': html_utils.clean(getattr(data, 'post_excerpt', '')),
                    'guid': f'{consts.PRAGALERIA_AUCTIONS_URL}{parent.post_name}',
                    'date': str(getattr(data, 'post_modified', '')),
                    'auction_start': auction_start,
                    'auction_end': auction_end,
                    'auction_status': bool(int(postmeta.by_key(parent.id, 'aukcja_status', '0'))),
                    **thumbnails.by_id(parent_id)
                }