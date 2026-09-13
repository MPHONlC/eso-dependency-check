# ESO Addon Dependency Version Check

Checks your manifest's declared `## DependsOn: <Name>>=<version>` floor for one named dependency against that dependency's actual current published `## AddOnVersion:` (fetched live from its own repo's raw manifest URL) - catches a forgotten `DependsOn` bump after the dependency releases an update.

Single-dependency, called once per library you want checked - compose multiple steps in your workflow for multiple dependencies rather than guessing which one "matters most."

## Usage

```yaml
name: Dependency Version Check

on:
  schedule:
    - cron: '0 12 * * *'
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: MPHONlC/eso-dependency-check@Version-0.0.1
        with:
          manifest_file: 'YourAddon.addon'
          dependency_name: 'LibAPH'
          dependency_manifest_url: 'https://raw.githubusercontent.com/MPHONlC/LibAPH/main/LibAPH.addon'
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `manifest_file` | Yes | - | Your own `.addon` manifest. |
| `dependency_name` | Yes | - | Name of the dependency to check - must match exactly what appears in your `DependsOn` line. |
| `dependency_manifest_url` | Yes | - | Raw URL to the dependency's own live `.addon` manifest. |

## What triggers what

| Condition | Result |
|---|---|
| Declared floor < dependency's actual published version | **Fails** the run - you're under-declaring; bump `DependsOn`. |
| Declared floor > dependency's actual published version | **Warns** but doesn't fail - unusual (could be a typo, or a forward-declared floor for a dependency version that isn't published yet), worth a manual look. |
| Declared floor == dependency's actual published version | Passes silently. |

## License

MIT - see [LICENSE](LICENSE).
