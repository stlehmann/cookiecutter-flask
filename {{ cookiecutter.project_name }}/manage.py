"""Manage deployment, backup and restore.

:author: Stefan Lehmann <stlm@posteo.de>
:license: MIT, see license file or https://opensource.org/licenses/MIT

:created on 2019-05-31 09:00:51
:last modified by:   stefan
:last modified time: 2019-06-09 13:20:49

"""
import pathlib
import shutil
import tempfile
import tarfile
import click
import subprocess
import sys
from fabric import Connection


{% if cookiecutter.docker_registry %}
DOCKER_REGISTRY = "{{ cookiecutter.docker_registry }}"
{% else %}
DOCKER_REGISTRY = None
{% endif %}

# If you use an own docker registry you need to specify here
# DOCKER_REGISTRY = "registry.mrl33h.de"

# The name of the docker image
{% if cookiecutter.docker_image %}
DOCKER_IMAGE = "{{ cookiecutter.docker_image }}"
{% else %}
DOCKER_IMAGE = None
{% endif %}


def checked_call(cmd):
    """Check returncode."""
    ret = subprocess.call(cmd)
    if ret != 0:
        click.echo(
            click.style(
                f"Error processing command \"{' '.join(cmd)}\", returncode={ret}",
                fg="red",
            )
        )
        sys.exit(1)


class AbstractHost:
    def __init__(self, host, directory):
        self.host = host
        self.directory = directory

    def deploy(self):
        pass

    def backup(self, filename):
        pass

    def restore(self, filename):
        pass


class LocalHost(AbstractHost):
    def deploy(self, host):
        pass

    def backup(self, host, dst):
        app_p = pathlib.Path("./app")
        dst_p = pathlib.Path(dst)

        if dst_p.is_file():
            dst_p.unlink()

        tar = tarfile.open(dst, mode="w:gz")
        tar.add(app_p / "db", "db")
        tar.add(app_p / "static" / "images", "images")
        tar.close()

    def restore(self, host, src):
        app_p = pathlib.Path() / "app"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_p = pathlib.Path(tmpdir)

            with tarfile.open(src, "r:gz") as tar:
                tar.extractall(tmpdir_p)

            shutil.rmtree(app_p / "db", ignore_errors=True)
            shutil.copytree(tmpdir_p / "db", app_p / "db")

            shutil.rmtree(app_p / "static/images", ignore_errors=True)
            shutil.copytree(tmpdir_p / "images", app_p / "static/images")


class RemoteHost(AbstractHost):

    def deploy(self, host):
        c = Connection(host)
        checked_call(["docker-compose", "build"])
        checked_call(["docker-compose", "push", "flask"])
        c.run(f"docker login {DOCKER_REGISTRY}")
        c.run(f"docker pull {DOCKER_IMAGE}")
        c.run(f"cd {self.directory} && docker-compose down")
        c.run(f"cd {self.directory} && docker-compose up -d")

    def backup(self, host, dst):
        c = Connection(host)
        c.run(f"cd {self.directory} && tar -cvzf backup.tgz db images")
        c.get(f"{self.directory}/backup.tgz", dst)
        c.run(f"rm {self.directory}/backup.tgz")

    def restore(self, host, src):
        c = Connection(host)
        c.put(src, f"{self.directory}/backup.tgz")
        c.run(f"cd {self.directory} && docker-compose stop")
        c.run(f"cd {self.directory} && rm -rf db images", warn=True)
        c.run(f"cd {self.directory} && tar -xvzf backup.tgz")
        c.run(f"rm {self.directory}/backup.tgz")
        c.run(f"cd {self.directory} && docker-compose start")


hosts = dict(
    localhost=LocalHost("localhost", "."),
    {% if cookiecutter.remote_host %}
    remote=RemoteHost("{{ cookiecutter.remote_host }}", "{{ cookiecutter.remote_directory }}")
    {% endif %}
)


@click.group()
def cli():
    pass


@cli.command()
@click.option("-h", "--host", type=click.Choice(hosts.keys()))
def deploy(host):
    """Deploy application to host."""
    hosts[host].deploy(host)


@cli.command()
@click.option("-h", "--host", type=click.Choice(hosts.keys()))
@click.argument("dst", type=click.types.Path())
def backup(host, dst):
    """Backup application data to file."""
    hosts[host].backup(host, dst)


@cli.command()
@click.option("-h", "--host", type=click.Choice(hosts.keys()))
@click.argument("src", type=click.types.Path())
def restore(host, src):
    """Restore application data from file."""
    hosts[host].restore(host, src)


if __name__ == "__main__":
    cli()
