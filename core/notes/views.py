from core.notes.admin import admin
from core.notes import app
from flask.views import View
from flask.views import MethodView
from flask_login import login_required
from core.notes.models import Notes, Tags
from core.accounts.models import Admin1
from sqlalchemy import desc, or_
from flask_paginate import Pagination, get_page_parameter
from flask import request, render_template, jsonify, url_for
from core.models import db
from datetime import datetime, timedelta


class Index(View):
    methods = ["GET"]
    init_every_request = False
    decorators = [login_required]

    def dispatch_request(
        self,
    ):
        notes = Notes.query.order_by(desc(Notes.created_on)).all()
        per_page = 14
        page_no = request.args.get(
            get_page_parameter(),
            type=int,
            default=1,
        )
        pagination = Pagination(
            total=len(notes), page=page_no, record_name="notes", per_page=per_page
        )
        return render_template("notes/index.html", **locals())


class NotesView(MethodView):
    methods = ["GET"]
    init_every_request = False
    decorators = [login_required]

    def __init__(self, *args, **kwargs):
        pass

    def get(self, id):
        note = Notes.query.filter_by(id=id).first_or_404()
        note.views += 1
        db.session.commit()
        recent_notes = Notes.query.order_by(desc(Notes.created_on)).limit(7).all()
        related_notes = (
            Notes.query.filter(
                Notes.tags.any(Tags.name.in_([tag.name for tag in note.tags]))
            )
            .filter(Notes.id != note.id)
            .order_by(desc(Notes.created_on))
            .limit(10)
            .all()
        )
        return render_template("notes/note_view.html", **locals())


class TagView(View):
    methods = ["GET"]
    init_every_request = False
    decorators = [login_required]

    def dispatch_request(self, tag):
        notes = (
            Notes.query.filter(Notes.tags.any(Tags.name.in_([tag])))
            .order_by(desc(Notes.created_on))
            .limit(10)
            .all()
        )
        pagination = Pagination(
            total=len(notes),
            page=request.args.get(
                get_page_parameter(),
                type=int,
                default=1,
            ),
            record_name="notes",
            per_page=14,
        )
        return render_template("notes/index.html", **locals())


class PinnedView(View):
    methods = ["GET"]
    init_every_request = False
    decorators = [login_required]

    def dispatch_request(self):
        notes = (
            Notes.query.filter_by(is_pinned=True)
            .order_by(desc(Notes.created_on))
            .limit(10)
            .all()
        )
        page_no = request.args.get(
            get_page_parameter(),
            type=int,
            default=1,
        )
        per_page = 14
        pagination = Pagination(
            total=len(notes), page=page_no, record_name="notes", per_page=per_page
        )
        return render_template("notes/index.html", **locals())


class TimeView(View):
    methods = ["GET"]
    init_every_request = False
    decorators = [login_required]

    def dispatch_request(self, days):
        notes = (
            Notes.query.filter(
                Notes.created_on > datetime.utcnow() - timedelta(days=days)
            )
            .order_by(desc(Notes.created_on))
            .limit(10)
            .all()
        )
        page_no = request.args.get(
            get_page_parameter(),
            type=int,
            default=1,
        )
        per_page = 14
        pagination = Pagination(
            total=len(notes), page=page_no, record_name="notes", per_page=per_page
        )
        return render_template("notes/index.html", **locals())


class SearchView(MethodView):
    methods = ["GET", "POST"]
    decorators = [login_required]
    init_every_request = True

    def get_filters(self, q, f):
        q = f"%{q}%"
        filters = {
            "any": or_(
                Notes.title.like(q),
                Notes.content.like(q),
                Notes.created_on.like(q),
                Notes.intro.like(q),
                Notes.file.like(q),
                Notes.author.any(
                    Admin1.name.like(q),
                ),
                Notes.tags.any(
                    Tags.name.like(q),
                ),
            ),
            "title": Notes.title.like(q),
            "content": or_(
                Notes.content.like(q),
                Notes.intro.like(q),
            ),
            "file": Notes.file.like(q),
            "time": Notes.created_on.like(q),
            "intro": Notes.intro.like(q),
            "author": Notes.author.any(
                Admin1.name.like(q),
            ),
            "tag": Notes.tags.any(
                Tags.name.like(q),
            ),
        }
        return filters[f if f in filters else "any"]

    def get(self):
        query = request.args.get("q", "")
        filter = request.args.get("f", "any")
        display = request.args.get("d", type=int, default=7)
        raw_resp = (
            Notes.query.filter(self.get_filters(query, filter))
            .order_by(desc(Notes.created_on))
            .with_entities(Notes.id, Notes.title, Notes.created_on)
            .limit(display)
            .all()
        )
        resp = []
        for entry in raw_resp:
            resp.append([url_for("notes1.note_view", id=entry[0]), entry[1], entry[2]])
        return jsonify(dict(result=resp))

    def post(self):
        query = request.form.get("q", "")
        filter = request.form.get("filter", "any")
        notes = (
            Notes.query.filter(
                self.get_filters(
                    query,
                    filter,
                )
            )
            .order_by(desc(Notes.created_on))
            .all()
        )
        page_no = request.args.get(
            get_page_parameter(),
            type=int,
            default=1,
        )
        pagination = Pagination(
            total=len(notes), per_page=14, page=page_no, record_name="notes"
        )
        return render_template("notes/index.html", **locals())


app.add_url_rule("/", view_func=Index.as_view("index"))
app.add_url_rule("/<int:id>", view_func=NotesView.as_view("note_view"))
app.add_url_rule(
    "/<tag>",
    view_func=TagView.as_view(
        "tag_view",
    ),
)
app.add_url_rule("/pinned", view_func=PinnedView.as_view("pinned_view"))
app.add_url_rule("/time/<int:days>", view_func=TimeView.as_view("time_view"))
app.add_url_rule("/search", view_func=SearchView.as_view("search_view"))
