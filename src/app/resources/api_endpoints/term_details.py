from flask_restful import Resource, abort

from app.api_utils.regex_utils import get_dimensions_from_description
from app.models import models
from app.api_utils import thumbnails, postmeta, html_utils


class TermDetails(Resource):
    def get(self, term_id=None):
        if term_id is not None:
            author = self.build_object(term_id)
            if author:
                return author

        abort(404, message='Author does not exist. id: {}'.format(term_id))

    def build_object(self, term_id):
        term, relationships, taxonomy = self._get_term_details(term_id)
        if term and taxonomy:
            term_name = getattr(term, 'name', '')
            artworks = self._build_artworks(relationships, term_name)
            result = {
                'id': term_id,
                'name': term_name,
                'slug': getattr(term, 'slug', ''),
                'description': html_utils.clean(getattr(taxonomy, 'description', '')),
                'artworks': artworks,
                'image_thumbnail': ''
            }
            if len(artworks) > 0:
                result['image_thumbnail'] = artworks[0]['image_thumbnail']
                for artwork in artworks:
                    description = artwork.get('description', '')
                    dimensions = get_dimensions_from_description(description)
                    artwork["meta"] = {"dimension": dimensions}
            return result

    def _get_term_details(self, term_id):
        term = models.Terms.query.filter_by(
            term_id=term_id
        ).first()
        taxonomy = models.TermTaxonomies.query.filter_by(
            term_id=term_id,
        ).first()
        if taxonomy:
            relationships = models.TermRelationships.query.filter_by(
                term_taxonomy_id=taxonomy.term_taxonomy_id
            ).all()
        else:
            relationships = []

        return term, relationships, taxonomy

    def _build_artworks(self, artwork_candidates, term_name):
        artworks, titles = [], []
        for artwork in artwork_candidates:
            artwork_id = artwork.object_id
            artwork_post = models.Posts.query.filter_by(
                id=artwork_id
            ).first()
            if artwork_post and hasattr(artwork_post, 'post_title'):
                if artwork_post.post_title not in titles:
                    titles.append(artwork_post.post_title)
                    artworks.append(self._get_artwork_from_post(artwork_post, term_name))
        return artworks

    def _get_artwork_from_post(self, artwork_post, term_name=''):
        artwork_id = artwork_post.id

        result = {
            'id': artwork_id,
            'title': getattr(artwork_post, 'post_title', ''),
            'author': term_name,
            'description': html_utils.clean(getattr(artwork_post, 'post_content', '')),
            'sold': bool(int(postmeta.by_key(artwork_id, 'oferta_status', '0'))),
            'initial_price': postmeta.by_key(artwork_id, 'oferta_cena', ''),
            'sold_price': postmeta.by_key(artwork_id, 'oferta_cena_sprzedazy', ''),
            'year': postmeta.by_key(artwork_id, 'oferta_rok', ''),
            **thumbnails.by_id(artwork_id)
        }

        return result
