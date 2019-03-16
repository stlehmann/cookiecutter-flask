"""Main entrypoint to the application.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-03-12 19:28:54
:last modified by:   stefan
:last modified time: 2019-03-15 17:49:21

"""
from app import create_app
application = app = create_app()
