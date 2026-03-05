from app import db, create_app
from app.main.models import Mutation, Admin
import sqlalchemy as sqla
import sqlalchemy.orm as sqlo
from config import Config

app = create_app(Config)

@app.shell_context_processor
def make_shell_context():
    return {'sqla': sqla, 'sqlo': sqlo, 'db': db, 'Mutation': Mutation, 'Admin' : Admin}


@app.before_request
def initDB(*args, **kwargs):
    if app._got_first_request:
        db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=3000)

    