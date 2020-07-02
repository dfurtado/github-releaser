import click
import os

from github_releaser import GithubReleaser


@click.command(name="upload-assets", help="Upload assets to a existent release")
@click.option("--account", "--a", required=True, help="Account")
@click.option("--repository", "--r", required=True, help="Repository")
@click.option("--token", help="GitHub's API token")
@click.option("--tag-name", "--t", required=True, help="The release tag")
@click.argument("assets", nargs=-1, type=str)
def upload_assets(account, repository, token, tag_name, assets):

    access_token = token or os.getenv("GITHUB_TOKEN", None)

    if not access_token:
        print(
            "access token is required. Use --token or set GITHUB_TOKEN in our environment"
        )

    gh = GithubReleaser(account, repository, access_token)
    gh.upload_assets(tag_name, assets)
