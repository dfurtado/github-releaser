import requests

from os import path
from http import HTTPStatus
from typing import Any, List
from yaspin import yaspin
from base64 import b64encode
import urllib.parse
import json

from .exceptions import ReleaseError, UploadError, ArgumentError
from .release import Release


API_BASEURL = "https://api.github.com"
MAX_UPLOAD = 10


def _validate_required(arg_name: str, value: str) -> None:
    if not value:
        raise ArgumentError("field is required: {}".format(arg_name))


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
        with yaspin(text="Creating release {}".format(tag_name)) as spinner:
            data = {
                "tag_name": tag_name,
                "name": name if name else tag_name,
                "target_commitish": target_commitish,
                "body": "",
            }

            url = "{}/repos/{}/{}/releases".format(API_BASEURL, self._account, self._repository)

            response = requests.post(url, json=data, auth=self.auth)

            if response.status_code != HTTPStatus.CREATED:
                spinner.fail()
                raise ReleaseError("Could not create the release {}".format(tag_name))

            response_json = response.json()
            spinner.ok()
            return response_json

    def _get_release_upload_url(self, tag_name: str):
        """ Get a release and returns its upload_url for uploading assets
        Github API: GET /repos/:owner/:repo/releases/tags/:tag """

        release = self._releases.get(tag_name, None)
        if release:
            return release.upload_url
        url = "{}/repos/{}/{}/releases/tags/{}".format(API_BASEURL, self._account, self._repository, tag_name)
        response = requests.get(url, auth=self.auth)
        response_json = response.json()

        if not response.ok:
            raise UploadError(
                "Could not get the upload URL. {} (Code: {})".format(response_json.get("message", None), response.status_code))

        url = response_json.get("upload_url", None)
        if url:
            url = url[0 : url.index("{")]

        self._cache_release_info(response_json)
        return url

    def upload_assets(self, tag_name: str, files: List[str]) -> None:
        """ Upload assets to a specified release
        Github API: POST :server/repos/:owner/:repo/releases/:release_id/assets{?name,label}"""

        if len(files) > MAX_UPLOAD:
            raise ArgumentError("cannot upload more than {} files".format(MAX_UPLOAD))

        with yaspin(text="Checking release for tag {}".format(tag_name)) as spinner:
            upload_url = self._get_release_upload_url(tag_name)
            if not upload_url:
                raise ArgumentError(
                    "Could not get the upload URL or the release with tag {} does not exist".format(tag_name)
                )
            spinner.ok()

        headers = {
            "Content-type": "application/octet-stream",
        }

        with yaspin(text="Uploading asset") as spinner:
            for file in files:
                abspath = path.abspath(file)
                filename = path.basename(abspath)
                url = "{}?name={}".format(upload_url, filename)

                spinner.write(
                    "Uploading '{}' to '{}/{}/{}'".format(abspath, self._account, self._repository, tag_name)
                )

                with open(abspath, "rb") as f:
                    file_data = f.read()

                    response = requests.post(
                        url, data=file_data, headers=headers, auth=self.auth
                    )

                    if response.status_code != HTTPStatus.CREATED:
                        spinner.fail()
                        raise UploadError("Could not upload the file")

                    spinner.write("Upload complete")
                spinner.ok()

    def push_files(self, branch_name: str, dest_dir: str, message: str, files: List[str]) -> None:
        """ Push new files to a specified branch
        Github API: PUT /repos/:owner/:repo/contents/:path"""

        if len(files) > MAX_UPLOAD:
            raise ArgumentError(
                "cannot push more than {} files".format(MAX_UPLOAD))

        with yaspin(text="Checking the branch exists {}".format(branch_name)) as spinner:

            url = "{}/repos/{}/{}/branches/{}".format(
                API_BASEURL, self._account, self._repository, branch_name)
            response = requests.get(url, auth=self.auth)
            if not response.ok:
                raise ArgumentError(
                    "Could not get the branch {}".format(branch_name)
                )
            spinner.ok()

        with yaspin(text="Pushing the files") as spinner:
            for file in files:
                abspath = path.abspath(file)
                filename = path.basename(abspath)
                destPath = filename
                if dest_dir:
                    destPath = "{}/{}".format(dest_dir, filename)

                url = "{}/repos/{}/{}/contents/{}".format(
                    API_BASEURL, self._account, self._repository, urllib.parse.quote(destPath))

                spinner.write(
                    "Pushing '{}' to '{}/{}/{}'".format(
                        abspath, self._account, self._repository, branch_name)
                )

                spinner.write(
                    "Verifying whether the file '{}' exists in '{}/{}/{}'".format(
                        destPath, self._account, self._repository, branch_name)
                )
                res = requests.get(
                    url, json={"ref": branch_name}, headers={"Content-type": "application/json"}, auth=self.auth
                )
                sha = ""
                if res.ok:
                    spinner.write(
                        "Updating the file '{}'".format(destPath))
                    result = json.loads(res.text)
                    sha = result.get("sha")
                else:
                    spinner.write(
                        "Adding the file '{}'".format(destPath))

                if not message:
                    if sha:
                        message = "Updated {}".format(destPath)
                    else:
                        message = "Added {}".format(destPath)

                with open(abspath, "rb") as f:
                    file_data = f.read()
                    file_data = b64encode(file_data).decode("utf-8")
                    put_parameters = {"branch": branch_name,
                                      "message": message,
                                      "content": file_data,
                                      "sha": sha}

                    headers = {
                        "Content-type": "application/json",
                    }
                    response = requests.put(
                        url, json=put_parameters, headers=headers, auth=self.auth
                    )

                    if response.ok or response.status_code != HTTPStatus.CREATED:
                        result = json.loads(response.text)
                        if sha == result["content"]["sha"]:
                            spinner.write(
                                "No changes in the file '{}' detected, did nothing".format(destPath))
                        else:
                            spinner.write(
                                "Pushed the file '{}'".format(destPath))
                    else:
                        spinner.fail()
                        result = json.loads(response.text)
                        raise UploadError(
                            "Could not push the file. {} (Code: {})".format(result.get("message"), response.status_code))

                spinner.ok()
