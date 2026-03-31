from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify, request
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash


def init_api(app, db, Article, User) -> None:
    """
    Подключает API в существующее Flask-приложение.
    """

    api_bp = Blueprint("api", __name__, url_prefix="/api")

    def _json_error(message: str, status: int = 400):
        return jsonify({"ok": False, "error": message}), status

    def _article_to_dict(article) -> dict[str, Any]:
        date_val = getattr(article, "date", None)
        return {
            "id": article.id,
            "title": article.title,
            "intro": article.intro,
            "text": article.text,
            "date": date_val.isoformat() if date_val is not None else None,
        }

    @api_bp.get("/news")
    def list_news():
        articles = Article.query.order_by(Article.date.desc()).all()
        return jsonify({"ok": True, "items": [_article_to_dict(a) for a in articles]})

    @api_bp.get("/news/<int:article_id>")
    def get_news(article_id: int):
        article = db.session.get(Article, article_id)
        if article is None:
            return _json_error("Article not found", 404)
        return jsonify({"ok": True, "item": _article_to_dict(article)})

    @api_bp.post("/auth/login")
    def login():
        payload = request.get_json(silent=True) or {}
        username = payload.get("username")
        password = payload.get("password")

        if not username or not password:
            return _json_error("username and password are required", 400)

        user = User.query.filter_by(username=username).first()
        if user is None:
            return _json_error("User not found", 404)
        if not check_password_hash(user.password, password):
            return _json_error("Invalid credentials", 401)

        login_user(user)
        return jsonify({"ok": True, "message": "Login successful"})

    def _require_admin():
        if not current_user.is_authenticated:
            return _json_error("Authentication required", 401)
        if not getattr(current_user, "admin", False):
            return _json_error("Admin privileges required", 403)
        return None

    @api_bp.post("/news")
    def create_news():
        err = _require_admin()
        if err is not None:
            return err

        payload = request.get_json(silent=True) or {}
        title = payload.get("title")
        intro = payload.get("intro")
        text = payload.get("text")

        if not title or not intro or not text:
            return _json_error("title, intro, text are required", 400)

        article = Article(title=title, intro=intro, text=text)
        db.session.add(article)
        db.session.commit()
        return jsonify({"ok": True, "item": _article_to_dict(article)}), 201

    @api_bp.delete("/news/<int:article_id>")
    def delete_news(article_id: int):
        err = _require_admin()
        if err is not None:
            return err

        article = db.session.get(Article, article_id)
        if article is None:
            return _json_error("Article not found", 404)

        db.session.delete(article)
        db.session.commit()
        return jsonify({"ok": True, "message": "Deleted"})

    # Регистрируем blueprint в приложение
    app.register_blueprint(api_bp)

