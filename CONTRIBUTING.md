# Contribution Guide

This is the official guide for contributing to the `seekcamera-python` project.

This project was created in the spirit of growing the Seek Thermal software ecosystem in an organic, positive way.
Anyone wishing to contribute to the project should read this document first.

## What we are looking for

All kinds of things!
We are always looking for contributions.

Find an issue, think of a new feature, or have an improvement? We courage you to submit a pull request.
Not a developer? We like help with testing and documentation too.

## Note on authoring changes

We use the Developer Certificate of Origin (DCO) in lieu of a Contributor License Agreement for all contributions to Seek Thermal’s open source projects.
Please make sure you understand the terms of the [DCO](./DCO) before contributiing.

## Versioning

We use a three digit versioning scheme.
At the moment, there is not a set release cadence -- as this project grows, we will consider setting one.

```txt
[major].[minor].[patch]
```

Releases generally increment the `minor` version number.
The `major` version number is only incremented for major changes.
The `patch` version number is incremented for patched releases that do not introduce new features.

## Branching

The top-of-tree branch is `main`.
Release tags are created on this branch.

If you are submitting a pull request, please submit it to `main`.

### Creating a branch

The first step in making a code change is to create a new branch.

```bash
# Use main as the starting branch
git checkout main

# Create a branch
git checkout -b feature-my-change
```

### Making commits

Commit messages should be clear and use imperative language.

Note that we use the [Protobot DCO](https://github.com/apps/dco) GitHub app to check for DCO signoffs of every commit.
The Protobot DCO app will provide instructions on how to ammend your commits if it catches an issue; to stay ahead of the curve please sign all commits with the `-s` flag.

```txt
git commit -s
```

### Keeping the branch up to date

The starting branch may change while making a change.
If you have a long lived branch, it is recommended to keep it up to date.
Use no fast-forward merging to create a merge commit.

```bash
git pull

git checkout feature-my-change

git merge --no-ff origin/main
```

### Pushing to the remote

```bash
git push -u origin feature-my-change
```

## Pull requests

The mechanism to get a code change merged is via pull requests (PRs).
The following guidelines should be followed when submitting a PR:
* Clear and imperative description of what is being changed and why
    * This helps save time in reviewing; it also helps others navigate the history.
* Doc strings for public methods
    * This is how we document our APIs.
* Testing of all sample applications
    * We require all changes be thoroughly tested before submitting a PR.
    We understand that you may have limited hardware -- that is okay.
    Test with what you have and let us know what tests were run and on what hardware.
* Any additional unit testing
    * We are always thrilled to see more tests!
* Passing of all CI actions
    * GitHub will warn you in the PR page if any fail.
* Sign off all commits as in compliance with the [DCO](./DCO)
* No merge conflicts
    * If you are unsure of how to resolve a conflict we can help.

## Style guide

We use [black](https://pypi.org/project/black/) for code formatting.
One of the GitHub Actions will check formatting when opening a PR.

```txt
# Install black
pip3 install black

# Run black in the current directory
black .
```