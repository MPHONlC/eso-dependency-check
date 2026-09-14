# ESO Addon Dependency Version Check

Checks your manifest's declared `## DependsOn: <Name>>=<version>` floor for one named dependency against that dependency's actual current published `## AddOnVersion:` - catches a forgotten `DependsOn` bump after the dependency releases an update.

Single-dependency, called once per library you want checked - compose multiple steps in your workflow for multiple dependencies.

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
      - uses: MPHONlC/eso-dependency-check@Version-0.0.2
        with:
          manifest_file: 'YourAddon.addon'
          dependency_name: 'LibAPH'
          dependency_manifest_url: 'https://raw.githubusercontent.com/MPHONlC/LibAPH/main/LibAPH.addon'
```

To auto-bump the floor instead of just failing:

```yaml
      - uses: MPHONlC/eso-dependency-check@Version-0.0.2
        with:
          manifest_file: 'YourAddon.addon'
          dependency_name: 'LibAPH'
          dependency_manifest_url: 'https://raw.githubusercontent.com/MPHONlC/LibAPH/main/LibAPH.addon'
          auto_update: true
          git_name: 'github-actions[bot]'
          git_email: 'github-actions[bot]@users.noreply.github.com'
```

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `manifest_file` | Yes | - | Your own `.addon` manifest. |
| `dependency_name` | Yes | - | Name of the dependency to check - must match exactly what appears in your `DependsOn`/`OptionalDependsOn` line. |
| `dependency_manifest_url` | Yes | - | Raw URL to the dependency's own live `.addon` manifest. |
| `auto_update` | No | `false` | If `true`, bump the declared floor to the dependency's actual version, commit, and push, instead of failing the run. |
| `git_name` | No | `''` | Git name for the auto-update commit - required if `auto_update` is `true`. |
| `git_email` | No | `''` | Git email for the auto-update commit - required if `auto_update` is `true`. |
| `skip_ci` | No | `true` | Append `[skip ci]` to the auto-update commit message. |

## What triggers what

| Condition | Result |
|---|---|
| Declared floor < dependency's actual published version, `auto_update` off | **Fails** the run - you're under-declaring; bump `DependsOn`/`OptionalDependsOn`. |
| Declared floor < dependency's actual published version, `auto_update` on | Bumps the floor, commits, pushes, and reports what changed - doesn't fail. |
| Declared floor > dependency's actual published version | **Warns** but doesn't fail - unusual (could be a typo, or a forward-declared floor for a dependency version that isn't published yet), worth a manual look. |
| Declared floor == dependency's actual published version | Passes silently. |

## License

MIT - see [LICENSE](LICENSE).
