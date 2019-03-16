"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-15 17:38:04
:last modified by:   stefan
:last modified time: 2019-03-15 18:07:55

"""
import subprocess
from app import create_app, db
from app.models import User, Role, Permission

subprocess.call(["flask", "db", "init"])

app = create_app()

with app.app_context():
    db.create_all()

    superuser_role = Role(name="Superuser", permissions=Permission.ADMINISTER)
    user_role = Role(name="User", default=True, permissions=Permission.MODIFY)

    admin_user = User(username="admin", password="admin", role=superuser_role)

    db.session.add(superuser_role)
    db.session.add(user_role)
    db.session.add(admin_user)
    db.session.commit()


subprocess.call(["flask", "db", "migrate"])
subprocess.call(["flask", "db", "upgrade"])
