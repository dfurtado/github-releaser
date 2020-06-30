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

## Copyright and License

Copyright (c) 2020 Daniel Furtado. Code released under MIT license

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
