import click
import os

from github_releaser import GithubReleaser


@click.command(name="prev-release-asset", help="Get previous release asset")
@click.option("--account", "--a", required=True, help="Account")
@click.option("--repository", "--r", required=True, help="Repository")
@click.option("--token", help="GitHub's API token")
@click.option("--asset", "--at", required=True, help="Asset name to download")
@click.option("--output", "--dir", help="Output directory for downloaded asset. Omit if downloading to the root")
def prev_release_asset(account, repository, token, asset, output):

    access_token = token or os.getenv("GITHUB_TOKEN", None)

    if not access_token:
        print(
            "access token is required. Use --token or set GITHUB_TOKEN in our environment"
        )

    gh = GithubReleaser(account, repository, access_token)
    gh.get_prev_release_asset(asset, output)
