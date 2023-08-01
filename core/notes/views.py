from core.notes.admin import admin
from core.notes import app
from flask.views import View
from flask.views import MethodView
from flask_login import login_required
from core.notes.models import Notes
from sqlalchemy import desc
from flask_paginate import Pagination, get_page_parameter
from flask import request, render_template

class Index(View):
	methods = ["GET"]
	init_every_request = False
	decorators = [login_required]
	
	def dispatch_request(self,):
		notes = Notes.query.order_by(desc(Notes.created_on)).all()
		pagination = Pagination(total = len(notes), page=request.args.get(get_page_parameter(), type=int, default=1,), record_name="notes", per_page=14,)
		return render_template('notes/index.html',**locals())

app.add_url_rule('/',view_func = Index.as_view('index'))