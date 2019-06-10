"""
:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-06-01 09:12:30
:last modified by:   stefan
:last modified time: 2019-06-09 13:43:56

"""
import sys
import fabric
import datetime
from subprocess import call


{% if cookiecutter.backup_server %}
SSH_SERVER = "{{ cookiecutter.backup_server }}"
{% else %}
SSH_SERVER = None
{% endif %}

if SSH_SERVER is None:
    sys.exit()

SSH_USERNAME = "{{ cookiecutter.backup_username }}"
KEEP_BACKUPS_FOR_DAYS = 10
DIRECTORIES = [
    "app/static/images",
    "app/db"
]

hostname = f"{SSH_USERNAME}@{SSH_SERVER}"

# Use rsync to backup files
for d in DIRECTORIES:
    call(["rsync", "-a", "--delete", d, f"{hostname}:backup"])


# Create new TAR file with content
now = datetime.datetime.utcnow()
filename = "backup_{0}.tgz".format(now.strftime("%Y%m%d_%H%M"))
c = fabric.Connection(hostname)
c.run(f"tar -czvf {filename} backup")


# Delete old tarfiles
{% raw %}
c.run(f"find * -mtime +{KEEP_BACKUPS_FOR_DAYS} -exec rm {{}} \;")
{% endraw %}
