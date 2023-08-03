from core.notes.admin import admin
from core.notes import app
from flask.views import View
from flask.views import MethodView
from flask_login import login_required
from core.notes.models import Notes, Tags
from sqlalchemy import desc
from flask_paginate import Pagination, get_page_parameter
from flask import request, render_template
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
    # methods = ["GET"]
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
