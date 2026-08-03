from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required
 
from app.modules.reports import services
 
reports_bp = Blueprint("reports", __name__, url_prefix="/reports")
 
 
def _require_instructor():
    if current_user.role != "instructor":
        abort(403)
 
 
@reports_bp.route("/")
@login_required
def index():
    _require_instructor()
 
    summary = services.get_dashboard_summary(current_user.id)
    reports = services.get_course_report(current_user.id)
 
    return render_template(
        "reports/index.html",
        summary=summary,
        reports=reports,
    )