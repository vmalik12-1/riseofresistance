from flask import render_template
from app import db

from app.errors import error_blueprint as errors

@errors.errorhandler(404)
def not_found_error(error):
    return render_template('404error.html'), 404

@errors.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500error.html'), 500