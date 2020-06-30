import os
import requests

from os import path
from http import HTTPStatus
from typing import Any, List
from yaspin import yaspin

from .exceptions import ReleaseError, UploadError, ArgumentError
from .release import Release


API_BASEURL = "https://api.github.com"
MAX_UPLOAD = 10


def _validate_required(arg_name: str, value: str) -> None:
    if not value:
        raise ArgumentError(f"field is required: {arg_name}")


class GithubReleaser:
    def __init__(self, account: str, repository: str, access_token: str):
        _validate_required("account", account)
        _validate_required("repository", repository)
        _validate_required("access_token", access_token)

        self._account = account
        self._repository = repository
        self._access_token = access_token

        self.auth = (account, access_token)

        self._releases = {}

    def _cache_release_info(self, release: Any) -> None:
        """ Caches the release information used by the script so it 
        minimize the number of requests to the github API"""

        tag_name = release["tag_name"]
        name = release["name"]
        upload_url = release["upload_url"]
        self._releases[tag_name] = Release(name, tag_name, upload_url)

    def create_release(
        self,
        tag_name: str,
        name: str = None,
        target_commitish: str = "master",
    ) -> Any:
        """ Create a new release on the specified repository
        Github API: POST /repos/:owner/:repo/releases """
        with yaspin(text=f"Creating release {tag_name}") as spinner:
            data = {
                "tag_name": tag_name,
                "name": name if name else tag_name,
                "target_commitish": target_commitish,
                "body": "",
            }

            url = f"{API_BASEURL}/repos/{self._account}/{self._repository}/releases"

            response = requests.post(url, json=data, auth=self.auth)

            if response.status_code != HTTPStatus.CREATED:
                spinner.fail()
                raise ReleaseError(f"Could not create the release {tag_name}")

            response_json = response.json()
            spinner.ok()
            return response_json

    def _get_release_upload_url(self, tag_name: str):
        """ Get a release and returns its upload_url for uploading assets
        Github API: GET /repos/:owner/:repo/releases/tags/:tag """

        release = self._releases.get(tag_name, None)
        if release:
            return release.upload_url

        url = f"{API_BASEURL}/repos/{self._account}/{self._repository}/releases/tags/{tag_name}"
        response = requests.get(url, auth=self.auth)
        response_json = response.json()
        url = response_json.get("upload_url", None)
        if url:
            url = url[0 : url.index("{")]

        self._cache_release_info(response_json)
        return url

    def upload_assets(self, tag_name: str, files: List[str]) -> None:
        """ Upload assets to a specified release
        Github API: POST :server/repos/:owner/:repo/releases/:release_id/assets{?name,label}"""

        if len(files) > MAX_UPLOAD:
            raise ArgumentError(f"cannot upload more than {MAX_UPLOAD} files")

        with yaspin(text=f"Checking release for tag {tag_name}") as spinner:
            upload_url = self._get_release_upload_url(tag_name)
            if not upload_url:
                raise ArgumentError(
                    f"Could not get the upload URL or the release with tag {tag_name} does not exist"
                )
            spinner.ok()

        headers = {
            "Content-type": "application/octet-stream",
        }

        with yaspin(text="Uploading asset") as spinner:
            for file in files:
                abspath = path.abspath(file)
                filename = path.basename(abspath)
                url = f"{upload_url}?name={filename}"

                spinner.write(
                    f"Uploading '{abspath}' to '{self._account}/{self._repository}/{tag_name}'"
                )

                with open(abspath, "rb") as f:
                    file_data = f.read()

                    response = requests.post(
                        url, data=file_data, headers=headers, auth=self.auth
                    )

                    if response.status_code != HTTPStatus.CREATED:
                        spinner.fail()
                        raise UploadError(f"Could not upload the file")

                    spinner.write(f"Upload complete")
                spinner.ok()
