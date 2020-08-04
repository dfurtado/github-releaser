import click
import os

from github_releaser import GithubReleaser


@click.command(name="push-files", help="Push new files to a branch")
@click.option("--account", "--a", required=True, help="Account")
@click.option("--repository", "--r", required=True, help="Repository")
@click.option("--token", help="GitHub's API token")
@click.option("--branch-name", "--b", default="master", help="The branch name.")
@click.option("--dest-dir", "--d", help="The destination subfolder inside the repository. Omit if pushing to the root")
@click.option("--message", "--m", help="The message. Default: Added/updated {file name}")
@click.argument("files", nargs=-1, type=str)
def push_files(account, repository, token, branch_name, dest_dir, message, files):

    access_token = token or os.getenv("GITHUB_TOKEN", None)

    if not access_token:
        print(
            "access token is required. Use --token or set GITHUB_TOKEN in our environment"
        )

    gh = GithubReleaser(account, repository, access_token)
    gh.push_files(branch_name, dest_dir, message, files)
