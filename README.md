# Virus Clade Utils

Virus Clade Utils is a wrapper around existing tools for downloading and working with virus genome sequences:

* The [NCBI Datasets API](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/rest-api/) provided by the National Institutes of Healh.
* The [Nexclade command line interface (CLI)](https://docs.nextstrain.org/projects/nextclade/en/stable/user/nextclade-cli/index.html) provided by [Nextstrain](https://docs.nextstrain.org/en/latest/).

This package was developed to provide data required for the [COVID-19 Variant Nowcast hub](https://github.com/reichlab/variant-nowcast-hub), where modelers and teams forecast the daily proportions of COVID-19 variants in US states.

We are releasing `virus-clade-utils` as a standalone package for use by others who may find the functionality useful.

TODO: Actual documentation

## Docker Setup

Use the directions below to run the pipeline in a Docker container.

**Prerequisites**

- Docker

**Setup**

1. Clone this repository and change into the high-level directory:

    ```bash
    cd virus-clade-utils
    ```
2. Build the Docker image:

    ```bash
    docker build --platform=linux/amd64 -t virus-clade-utils .
    ```

3. Run the pipeline, passing in required arguments:

    ```bash
    docker run --platform linux/amd64 \
    -v $(pwd)/data:/home/docker-user/ \
    virus-clade-utils \
    --sequence-released-since-date 2024-07-16 \
    --reference-tree-date 2024-07-16 \
    --data-dir /home/docker-user
    ```

The clade assignments will now be in the local directory that was mounted to the Docker container via the `-v` flag (in this case, a folder called `data` in the current working directory).

### Running the test suite

To run the test suite in the Docker container (built above):

1. Enter the container's bash shell:

    ```bash
    docker run --platform linux/amd64 -it --entrypoint bash virus-clade-utils
    ```

2. Once you're in the shell of the container, run the tests:

    ```bash
    pytest
    ```

(or `pytest -k unit` to run only the unit tests)

## Local Machine Setup

If you'd like to run or develop outside of Docker, this section has the setup instructions.

**Prerequisites**

Before setting up the project:

- Your machine will need to have an installed version of Python that meets the `requires-python` constraint in [pyproject.toml](pyproject.toml)
- That version of Python should be set as your current Python interpreter (if you don't already have a preferred Python workflow, [pyenv](https://github.com/pyenv/pyenv) is good tool for managing Python versions on your local machine).
- You will need to install two CLI tools used by the pipeline, and ensure they're available in your PATH:
    - [dataformat](https://www.ncbi.nlm.nih.gov/datasets/docs/v2/download-and-install/), to format sequence metadata
    - [Nextclade](https://docs.nextstrain.org/projects/nextclade/en/stable/user/nextclade-cli/installation/index.html), to assign clades to sequences

In addition, if you're planning to make code changes that require adding or removing project dependencies, you'll need `pip-tools` installed on your machine. ([`pipx`](https://github.com/pypa/pipx) is a handy way to install python packages in a way that makes them available all the time, regardless of whatever virtual environment is currently activated.)

**Setup**

Follow the directions below to set this project up on your local machine.

1. Clone this repository and change into the project's high-level directory:

    ```bash
    cd virus-clade-utils
    ```

2. Create a Python virtual environment:

    ```bash
    python -m venv .venv
    ```

    **Note:** the resulting virtual environment will use whatever Python interpreter was active when you ran the command

3. Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

    **Note:** the command above is for Unix-based systems. If you're using Windows, the command is:

    ```bash
    .venv\Scripts\activate
    ```

4. Install the project dependencies. The following command can also be used to update dependencies after pulling upstream code changes:

    ```bash

    pip install -r requirements/requirements-dev.txt && pip install -e .
    ```

### Running the test suite

To run the unit tests:

```bash
pytest -k unit
```

To run the full test suite, including an integration test that runs the pipeline end-to-end:

```bash
pytest
```

### Adding new dependencies

At a high-level, this is the process for adding (or removing) a project dependency:

- add/remove the dependency in `pyproject.toml`
- use [`pip-tools`](https://github.com/jazzband/pip-tools) to read the dependencies in `pyproject.toml` and output detailed requirements files

To add a new dependency:

1. Make sure `pip-tools` is installed and available to your virtual environment (if you want `pip-tools` to be available across all virtual environments on your machine, you can install it using [`pipx`](https://pipx.pypa.io/stable/)).

    ```bash
    pip install pip-tools
    ```

2. Add dependency to the `dependencies` section `pyproject.toml` (if it's a dev dependency,
add it to the `dev` section of `[project.optional-dependencies]`).

3. Regenerate the `requirements.txt` file (if you've only added a dev dependency, you can skip this step)
    ```bash
    pip-compile -o requirements/requirements.txt pyproject.toml
    ```

4. Regenerate the `requirements-dev.txt` file (even if you haven't added a dev dependency):
    ```bash
    pip-compile --extra dev -o requirements/requirements-dev.txt pyproject.toml
    ```

## Running the code

Set up the project as described above and make sure the virtual environment is activated. The code that downloads the Genbank
sequences and assigns them to clades is a command-line tool called `assign_clades`.

To see the options and other help information:

```bash
assign_clades --help
```

To download Genbank sequences that have been released since 2024-08-02 and assign clades to them using the SARS-Cov-2 reference tree as it looked on 2024-07-13:

```bash
assign_clades --sequence-released-since-date 2024-08-02 --reference-tree-date 2024-07-13
```
