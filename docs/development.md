# Development

## Layout

- `custom_components/genieacs/`: the integration. `api.py` is the NBI client, `coordinator.py` the 60-second
  poll, `config_flow.py` the setup form, `sensor.py`, `binary_sensor.py` and `button.py` the entities,
  `entity.py` the device registry entry, `const.py` the parameter paths and the fixed intervals.
  `strings.json` and `translations/en.json` hold the UI text.
- `tests/`: the pytest suite. `conftest.py` stubs the Home Assistant modules, so the tests run without
  installing Home Assistant.
- `docs/` and `mkdocs.yml`: this site.

## Run the tests

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-test.txt
.venv/bin/pytest tests/ -v --cov=custom_components
```

CI runs the same command on Python 3.12. Coverage goes to Codecov, which expects 90% for the project and for
each change ([`codecov.yml`](https://github.com/GeiserX/genieacs-ha/blob/main/codecov.yml)).

## Try it in Home Assistant

Copy `custom_components/genieacs` into the `config/custom_components/` directory of a test Home Assistant,
restart it, and add the integration. For devices without real hardware, run GenieACS with
[genieacs-container](https://geiserx.github.io/genieacs-container/) and simulated devices with
[genieacs-sim-container](https://github.com/GeiserX/genieacs-sim-container).

## Checks on every pull request

| Workflow | Job | What it checks |
|----------|-----|----------------|
| Tests | `test` | the pytest suite and its coverage |
| Validate | `validate-hacs` | the repository against HACS's rules |
| Validate | `validate-hassfest` | `manifest.json` and the translations against Home Assistant's rules |
| Docs | `build (strict)` | this site builds with no broken link, missing page or page left out of the nav |

## Build the docs

```bash
python3 -m venv .venv-docs
.venv-docs/bin/pip install -r docs/requirements-docs.txt
.venv-docs/bin/mkdocs serve
```

`mkdocs build --strict` is what the Docs workflow runs. A push to `main` that changes `docs/` or `mkdocs.yml`
publishes the site.

## Releases

A release is a GitHub release tagged `vX.Y.Z`, with the same version in
`custom_components/genieacs/manifest.json` (`v1.0.1` and `"version": "1.0.1"` today). HACS offers the newest
release to users as an update.

## Contributing

Open pull requests against `main`. Report security problems through the
[security policy](https://github.com/GeiserX/genieacs-ha/blob/main/SECURITY.md), never in a public issue.
