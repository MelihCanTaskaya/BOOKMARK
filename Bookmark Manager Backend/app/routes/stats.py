from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Bookmark
from urllib.parse import urlparse

stats_bp = Blueprint('stats', __name__, url_prefix='/api/bookmarks/stats')

@stats_bp.route('/most-visited-domains', methods=['GET'])
@jwt_required()
def most_visited_domains():
    user_id = int(get_jwt_identity())
    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()

    domain_visits = {}
    for bm in bookmarks:
        domain = urlparse(bm.url).netloc.lower()
        domain_visits[domain] = domain_visits.get(domain, 0) + bm.visits

    sorted_domains = sorted(domain_visits.items(), key=lambda x: x[1], reverse=True)

    return jsonify({'most_visited_domains': sorted_domains}), 200
