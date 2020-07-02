import click
import os

from github_releaser import GithubReleaser


@click.command(name="create-release", help="Create a new release")
@click.option("--account", "--a", required=True, help="Account")
@click.option("--repository", "--r", required=True, help="Repository")
@click.option("--token", help="GitHub's API token")
@click.option("--release-name", "--n", help="release name. If not specified tag will be used")
@click.option("--tag-name", "--t", required=True, help="The tag, eg: v1.0.0")
@click.option("--branch", "--b", default="master", help="branch to create the release")
def create_release(
    account, repository, token, release_name, tag_name, branch
):
    access_token = token or os.getenv("GITHUB_TOKEN", None)

    if not access_token:
        print(
            "access token is required. Use --token or set GITHUB_TOKEN in our environment"
        )

    gh = GithubReleaser(account, repository, access_token)
    gh.create_release(tag_name, release_name, branch)
