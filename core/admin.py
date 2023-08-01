from flask_admin import Admin, AdminIndexView
from flask_login import current_user
from flask import flash, redirect, url_for
from flask_admin.contrib.fileadmin import FileAdmin
from .app import FILES_DIR, application


class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "error")
        return redirect(url_for("accounts.login_user"))


class FileAdminView(FileAdmin):
    can_mkdir = True
    can_upload = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, *args, **kwargs):
        flash("You're not authorised to access that endpoint!", "error")
        return redirect(url_for("home"))


admin = Admin(
    application,
    name=application.config["APP_NAME"],
    index_view=CustomAdminIndexView(),
    template_mode=application.config["TEMPLATE_MODE"],
)

admin.add_view(FileAdminView(base_path=FILES_DIR, name="Files"))
