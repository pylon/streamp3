## How to contribute to Streamp3
Interested in contributing to Streamp3? We appreciate all kinds of help!

### Pull Requests
We gladly welcome pull requests.

Before making any changes, we recommend opening an issue (if it doesn’t
already exist) and discussing your proposed changes. This will let us give
you advice on the proposed changes. If the changes are minor, then feel free
to make them without discussion.

### Development Process
To make changes, fork the repo. Write code in this fork with the following
guidelines. Some of these checks are performed automatically by CI whenever
a branch is pushed. These automated checks must pass before a PR will be
merged. The checks can also be used in a commit/push hook with the following
script.

```bash
flake8 . || exit 1
(ls -1 */__init__.py | sed -r 's|/.*||' | xargs pylint -r n) || exit 1
python -m pytest || exit 1
```

#### Formatting
For better or worse, we use flake8 and pylint. This ensures consistent coding
conventions and sane formatting.

#### Testing
Streamp3 uses the `pytest` tool to run tests.

#### Test Coverage
We strive to keep test coverage as high as possible. You can run the following
to get test coverage in pytest.

```bash
pytest --cov=streamp3 --cov-report=term-missing
```
