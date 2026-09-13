import re
import sys
import argparse


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-file', required=True)
    parser.add_argument('--dependency-name', required=True)
    parser.add_argument('--dependency-manifest', required=True)
    args = parser.parse_args()

    own = read(args.manifest_file)
    dep = read(args.dependency_manifest)
    out = [f"## Dependency version check ({args.dependency_name})", ""]

    if own is None:
        print(f"::error::Could not read {args.manifest_file}")
        sys.exit(1)
    if dep is None:
        print(f"::error::Could not read {args.dependency_manifest}")
        sys.exit(1)

    depends_m = re.search(r'^##\s*DependsOn:\s*(.+)$', own, re.M)
    if not depends_m:
        print(f"::error::No '## DependsOn:' line found in {args.manifest_file}")
        sys.exit(1)

    floor_m = re.search(re.escape(args.dependency_name) + r'\s*>=\s*(\d+)', depends_m.group(1))
    if not floor_m:
        print(f"::error::'{args.dependency_name}' not found in DependsOn line: {depends_m.group(1)!r}")
        sys.exit(1)
    declared_floor = int(floor_m.group(1))

    dep_version_m = re.search(r'^##\s*AddOnVersion:\s*(\d+)', dep, re.M)
    if not dep_version_m:
        print(f"::error::No '## AddOnVersion:' line found in {args.dependency_manifest}")
        sys.exit(1)
    actual_version = int(dep_version_m.group(1))

    out.append(f"Declared floor: `{args.dependency_name}>={declared_floor}`")
    out.append(f"{args.dependency_name}'s actual current AddOnVersion: `{actual_version}`")
    out.append("")

    if declared_floor < actual_version:
        msg = f"{args.dependency_name} has published {actual_version}, but this addon still only requires >={declared_floor} - consider bumping DependsOn."
        out.append(f"**{msg}**")
        print(f"::error::{msg}")
        print('\n'.join(out))
        sys.exit(1)
    elif declared_floor > actual_version:
        msg = f"Declared floor ({declared_floor}) is HIGHER than {args.dependency_name}'s actual published version ({actual_version}) - unusual, worth double-checking (typo, or a forward-declared requirement for an unpublished dependency version)."
        out.append(f"**{msg}**")
        print(f"::warning::{msg}")
        print('\n'.join(out))
    else:
        out.append(f"Up to date - declared floor matches {args.dependency_name}'s actual current version.")
        print('\n'.join(out))


if __name__ == '__main__':
    main()
