import click

from .github_releaser import GithubReleaser
from .exceptions import ArgumentError, UploadError, ReleaseError
from .cmd import create_release, upload_assets


@click.group()
class cli:
    pass


cli.add_command(create_release)
cli.add_command(upload_assets)

if __name__ == "__main__":
    cli()