import click
import os

from github_releaser import GithubReleaser


@click.command(name="download-assets", help="Download release assets")
@click.option("--account", "--a", required=True, help="Account")
@click.option("--repository", "--r", required=True, help="Repository")
@click.option("--token", help="GitHub's API token")
@click.option("--tag-name", "--t", required=True, help="The tag, eg: v1.0.0")
@click.option("--out-dir", "--dir", default=".", help="Output directory for downloaded assets. Omit to place them to the current working directory")
@click.argument("assets", nargs=-1, type=str)
def download_assets(account, repository, token, tag_name, out_dir, assets):

    access_token = token or os.getenv("GITHUB_TOKEN", None)

    if not access_token:
        print(
            "access token is required. Use --token or set GITHUB_TOKEN in our environment"
        )

    gh = GithubReleaser(account, repository, access_token)
    gh.download_assets(tag_name, out_dir, assets)
