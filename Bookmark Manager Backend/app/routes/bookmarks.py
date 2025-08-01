from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from urllib.parse import urlparse
from app.models import Bookmark, Tag, BookmarkTag, db
from app.database import db
from app.models import Bookmark, Tag, BookmarkTag

bookmarks_bp = Blueprint('bookmarks', __name__, url_prefix='/api/bookmarks')

from sqlalchemy.orm import joinedload

@bookmarks_bp.route('/', methods=['GET'])
@jwt_required()
def get_bookmarks():
    user_id = int(get_jwt_identity())
    tag_name = request.args.get('tag')

    if tag_name:
        bookmarks = (
            Bookmark.query
            .options(joinedload(Bookmark.tags))  # burada join load eklendi
            .join(Bookmark.tags)
            .filter(Bookmark.user_id == user_id, Tag.name == tag_name)
            .all()
        )
    else:
        bookmarks = (
            Bookmark.query
            .options(joinedload(Bookmark.tags))  # burada join load eklendi
            .filter_by(user_id=user_id)
            .all()
        )

    result = []
    for b in bookmarks:
        tags = [t.name for t in b.tags] if hasattr(b, "tags") else []
        result.append({
            'id': b.id,
            'url': b.url,
            'title': b.title,
            'created_at': b.created_at.isoformat(),
            'tags': tags
        })

    return jsonify(result), 200



@bookmarks_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_single_bookmark(id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=id, user_id=user_id).first()
    
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404
    bookmark.visits = bookmark.visits or 0
    bookmark.visits += 1
    db.session.commit()
    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'title': bookmark.title,
        'created_at': bookmark.created_at.isoformat(),
        'Tags': [tag.name for tag in bookmark.tags] , # Assuming Bookmark has a relationship with Tag
        'visits': bookmark.visits
    }), 200


@bookmarks_bp.route('/', methods=['POST'])
@jwt_required()
def add_bookmark():
    user_id = int(get_jwt_identity())
    data = request.get_json(force=True)

    if not data:
        return jsonify({'error': 'Missing JSON in request'}), 400

    url = data.get('url')
    title = data.get('title', '')
    tags = data.get('tags', [])
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    existing_bookmark = Bookmark.query.filter_by(user_id=user_id, url=url).first()
    if existing_bookmark:
        return jsonify({'error': 'Bookmark already exists for this user'}), 400

    new_bm = Bookmark(url=url, title=title, user_id=user_id)
    db.session.add(new_bm)
    db.session.flush()  # id oluşması için

    # Tag ilişkilendirmeyi BookmarkTag ara tablosu modeli ile yap
    for tag_name in tags:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
            db.session.flush()
        bookmark_tag = BookmarkTag(bookmark_id=new_bm.id, tag_id=tag.id)
        db.session.add(bookmark_tag)

    db.session.commit()

    return jsonify({'message': 'Bookmark added', 'id': new_bm.id}), 201




# İstersen update, delete için de endpoints yazabiliriz.
@bookmarks_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_bookmark(id):
    user_id = int(get_jwt_identity())
    bookmark = Bookmark.query.filter_by(id=id, user_id=user_id).first()

    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({'message': 'Bookmark deleted'}), 200
# İstersen update için de bir endpoint ekleyebiliriz.
@bookmarks_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_bookmark(id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    print("Request JSON:", data)  
    url = data.get('url')
    title = data.get('title')

    bookmark = Bookmark.query.filter_by(id=id, user_id=user_id).first()

    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404

    if url:
        bookmark.url = url
    if title:
        bookmark.title = title

    db.session.commit()

    return jsonify({'message': 'Bookmark updated'}), 200

@bookmarks_bp.route('/<int:bookmark_id>/tags', methods=['POST'])
@jwt_required()
def add_tag_to_bookmark(bookmark_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tag_name = data.get('tag')

    if not tag_name:
        return jsonify({'error': 'Tag name is required'}), 400

    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404

    tag = Tag.query.filter_by(name=tag_name).first()
    if not tag:
        # Tag yoksa oluştur
        tag = Tag(name=tag_name)
        db.session.add(tag)
        db.session.commit()

    # İlişkinin zaten var olup olmadığını kontrol et
    existing_link = BookmarkTag.query.filter_by(bookmark_id=bookmark.id, tag_id=tag.id).first()
    if existing_link:
        return jsonify({'message': 'Tag already added to bookmark'}), 200

    # Yeni ilişki oluştur
    bookmark_tag = BookmarkTag(bookmark_id=bookmark.id, tag_id=tag.id)
    db.session.add(bookmark_tag)
    db.session.commit()

    return jsonify({'message': 'Tag added to bookmark'}), 201

@bookmarks_bp.route('/<int:bookmark_id>/tags/<int:tag_id>', methods=['DELETE'])
@jwt_required()
def remove_tag_from_bookmark(bookmark_id, tag_id):
    user_id = int(get_jwt_identity())
    
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404

    bookmark_tag = BookmarkTag.query.filter_by(bookmark_id=bookmark_id, tag_id=tag_id).first()
    if not bookmark_tag:
        return jsonify({'error': 'Tag not associated with bookmark'}), 404

    db.session.delete(bookmark_tag)
    db.session.commit()

    return jsonify({'message': 'Tag removed from bookmark'}), 200

@bookmarks_bp.route('/filter', methods=['GET'])
@jwt_required()
def get_bookmarks_by_tag():
    user_id = int(get_jwt_identity())
    tag_name = request.args.get('tag')

    if not tag_name:
        return jsonify({'error': 'Tag parameter is required'}), 400

    bookmarks = (
        Bookmark.query
        .join(Bookmark.tags)
        .filter(Bookmark.user_id == user_id)
        .filter(Tag.name == tag_name)
        .all()
    )

    result = [{
        'id': b.id,
        'url': b.url,
        'title': b.title,
        'created_at': b.created_at.isoformat()
    } for b in bookmarks]

    return jsonify(result), 200



@bookmarks_bp.route('/stats/most_visited', methods=['GET'])
@jwt_required()
def most_visited_bookmarks():
    user_id = int(get_jwt_identity())
    # user_id'ye ait bookmarkları visits sütununa göre azalan sırada al, limit 5
    bookmarks = Bookmark.query.filter_by(user_id=user_id).order_by(Bookmark.visits.desc()).limit(5).all()

    result = []
    for b in bookmarks:
        result.append({
            'id': b.id,
            'url': b.url,
            'title': b.title,
            'visits': b.visits,
            'created_at': b.created_at.isoformat()
        })
    return jsonify(result), 200

@bookmarks_bp.route("/grouped", methods=["GET"])
@jwt_required()
def get_bookmarks_grouped_by_tag():
    user_id = get_jwt_identity()

    grouped = {}

    bookmarks = Bookmark.query.filter_by(user_id=user_id).all()

    for bookmark in bookmarks:
        tag_names = [bt.tag.name for bt in bookmark.bookmark_tags]
        if not tag_names:
            grouped.setdefault("Untagged", []).append({
                "id": bookmark.id,
                "title": bookmark.title,
                "url": bookmark.url,
            })
        else:
            for tag in tag_names:
                grouped.setdefault(tag, []).append({
                    "id": bookmark.id,
                    "title": bookmark.title,
                    "url": bookmark.url,
                })

    return jsonify(grouped)

@bookmarks_bp.route('/<int:bookmark_id>/move', methods=['POST'])
@jwt_required()
def move_bookmark(bookmark_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    from_tag = data.get('from_tag')
    to_tag = data.get('to_tag')
    new_order = data.get('new_order', 0)

    # bookmark kontrolü
    bookmark = Bookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), 404

    # önce eski tag ilişkisini sil
    from_tag_obj = Tag.query.filter_by(name=from_tag).first()
    if from_tag_obj:
        bt = BookmarkTag.query.filter_by(bookmark_id=bookmark_id, tag_id=from_tag_obj.id).first()
        if bt:
            db.session.delete(bt)

    # yeni tag varsa, ilişkilendir
    to_tag_obj = Tag.query.filter_by(name=to_tag).first()
    if not to_tag_obj:
        to_tag_obj = Tag(name=to_tag)
        db.session.add(to_tag_obj)
        db.session.commit()

    # yeni ilişki ekle
    new_bt = BookmarkTag(bookmark_id=bookmark_id, tag_id=to_tag_obj.id, order=new_order)
    db.session.add(new_bt)
    db.session.commit()

    return jsonify({'message': 'Bookmark moved successfully'}), 200
@bookmarks_bp.route('/tag_order', methods=['POST'])
@jwt_required()
def update_tag_order():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    tag_order = data.get('tag_order', [])
    # Burada tag sırasını user'a göre kaydedebilirsin (ör: ayrı bir tabloya)
    # ...
    return jsonify({'message': 'Tag order updated'}), 200
