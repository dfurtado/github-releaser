# github-releaser

`github-releaser` is a command-line tool for creating releases on GitHub.

## Installation

`pipenv install github-releaser`

## Usage

### Creating a release

To create a release, use the command `create-release`, e.g.:
```shell script
github-releaser create-release --account myuser --repository myrepo --tag-name v1.0.10
```

The example above will create a new release with a name and tag set to `v1.0.10` at `myuser/myrepo`. The option 
`--release-name` is optional, and if not specified the release name will be the same as the value of the `--tag-name`, in 
this case: `v1.0.10`

To see all the options use: `github-releaser create-release --help`

### Uploading assets

The command `upload-assets` to add assets to a release. Note that to upload assets a release must have been previously
created.

Give that there is already a release `v1.0.10` at `myuser/myrepo`, it is possible to add assets with the following command:
```shell script
github-releaser upload-assets --account myuser --repository myrepo --tagname v1.0.10 assets/*.zip
```

The example above uploads all `.zip` files from the `assets` directory to a release `v1.0.10` at `myuser/myrepo`.

To see all the options use: `github-releaser upload-assets --help`

### Commit and push files to a branch

Sometimes it is useful to commit and push new files to a specific branch. One possible scenario is
when files are auto-generated during a build in a CI environment, and there is a requirement to
include them to a branch. For example:

```shell script
github-releaser push-files --account myuser --repository myrepo myfile.txt
```
In this example, a file named `myfile.txt` is added to the `master` at `myuser/myrepo`

To see all the options use: `github-releaser push-files --help`


### GitHub's personal access token

It is required to use a GitHub's personal access token to use the commands described above.
The personal access token can be passed directly in the command line using the option `--token` or
set to an environment variable called `GITHUB_TOKEN`.
More information on how to create a GitHub's token can
be found [here](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)

## Copyright and License

Copyright (c) 2020 Daniel Furtado. Code released under MIT license

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
