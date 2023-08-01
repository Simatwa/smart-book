from flask_admin.form import FileUploadField, SecureForm
#from flask_wtf.file import FileAllowed
from wtforms.validators import DataRequired
from .models import Notes, Tags
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from os import path
from core.app import FILES_DIR
from flask import redirect, url_for
from core.admin import admin
from core.notes.models import Notes, Tags
from core.admin import admin
from core.models import db
from flask_login import current_user

def filename_generator(obj, file_data):
	now = datetime.utcnow()
	return path.join(obj.tags[0].name, str(now.year), str(now.month),file_data.filename)
	
class NotesModelView(ModelView):
	page_size = 50
	can_export = True	
	can_create = True
	can_edit = True
	can_delete = True
	can_view_details = True	
	column_display_pk = True
	form_base_class = SecureForm	
	form_excluded_columns = ["created_on", "lastly_modified"]
	column_exclude_list = ["content"]
	column_filters = ["title","content","created_on","lastly_modified"]
	column_searchable_list = ["title","content","file"]
	
	form_args = {
	
	  "title" : {
	    "render_kw" : {
	     "placeholder" : "Note's title",
	    },
	  },
	  
	  "content" : {
	   "render_kw" : {
	    "placeholder" : "Contents here...",
	   },
	  },
	  
	  "tags" : {
	    "validators" : [ DataRequired(message="Cannot be null!",)],
	  },	  	  	  	  	  	  	  	  
	  
	}
	
	form_widget_args = {"content": {"rows": 20,},}
	form_extra_fields = {"file" : FileUploadField(label = "Attach file",base_path=FILES_DIR, namegen = filename_generator,),}
	
	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin
		
	def inaccessible_callback(self, *args, **kwargs):
	       flash("You're not authorised to access that endpoint!", "danger")
	       return redirect(url_for("home"))

  
class TagsModelView(ModelView):
	page_size = 50
	can_export = True
	can_create = True
	can_edit = True
	can_delete = True
	can_view_details = True
	column_display_pk = True
	form_base_class = SecureForm
	column_filters = ["name","created_on",]
	form_excluded_columns = ["created_on",]
	column_searchable_list = ["name","highlight",]
	
	form_args = {
	 "name" : {
	   "render_kw" : {
	     "placeholder" : "Tag slang",
	   },
	 },
	 
	 "highlight" : {
	  "render_kw" : {
	    "placeholder" : "Any relevant info related...",
	  },
	 },
	 
	}

	def is_accessible(self):
		return current_user.is_authenticated and current_user.is_admin
		
	def inaccessible_callback(self, *args, **kwargs):
	       flash("You're not authorised to access that endpoint!", "danger")
	       return redirect(url_for("home"))

admin.add_view(NotesModelView(Notes, db.session, name ='Notes', ))
admin.add_view(TagsModelView(Tags, db.session, name ='Tags',))		