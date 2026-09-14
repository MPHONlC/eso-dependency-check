import os
import re
import sys
import argparse
import subprocess


def read(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return None


def find_depends_line(text, dependency_name):
    for keyword in ('DependsOn', 'OptionalDependsOn'):
        m = re.search(r'^##\s*' + keyword + r':\s*(.+)$', text, re.M)
        if m and re.search(re.escape(dependency_name) + r'\s*>=\s*\d+', m.group(1)):
            return keyword, m
    return None, None


def bump_manifest(text, keyword, dependency_name, new_version):
    pattern = re.compile(r'(^##\s*' + keyword + r':\s*.*?' + re.escape(dependency_name) + r'\s*>=\s*)(\d+)', re.M)
    return pattern.sub(lambda m: m.group(1) + str(new_version), text, count=1)


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest-file', required=True)
    parser.add_argument('--dependency-name', required=True)
    parser.add_argument('--dependency-manifest', required=True)
    parser.add_argument('--auto-update', action='store_true')
    parser.add_argument('--git-name', default='')
    parser.add_argument('--git-email', default='')
    parser.add_argument('--skip-ci', default='true')
    args = parser.parse_args()

    annotations = []
    out = [f"## Dependency version check ({args.dependency_name})", ""]

    own = read(args.manifest_file)
    dep = read(args.dependency_manifest)

    if own is None:
        annotations.append(f"::error::Could not read {args.manifest_file}")
        emit(out, annotations)
        sys.exit(1)
    if dep is None:
        annotations.append(f"::error::Could not read {args.dependency_manifest}")
        emit(out, annotations)
        sys.exit(1)

    keyword, depends_m = find_depends_line(own, args.dependency_name)
    if not depends_m:
        annotations.append(f"::error::'{args.dependency_name}' not found in any 'DependsOn'/'OptionalDependsOn' line in {args.manifest_file}")
        emit(out, annotations)
        sys.exit(1)

    floor_m = re.search(re.escape(args.dependency_name) + r'\s*>=\s*(\d+)', depends_m.group(1))
    declared_floor = int(floor_m.group(1))

    dep_version_m = re.search(r'^##\s*AddOnVersion:\s*(\d+)', dep, re.M)
    if not dep_version_m:
        annotations.append(f"::error::No '## AddOnVersion:' line found in {args.dependency_manifest}")
        emit(out, annotations)
        sys.exit(1)
    actual_version = int(dep_version_m.group(1))

    out.append(f"Declared floor: `{args.dependency_name}>={declared_floor}`")
    out.append(f"{args.dependency_name}'s actual current AddOnVersion: `{actual_version}`")
    out.append("")

    if declared_floor < actual_version:
        msg = f"{args.dependency_name} has published {actual_version}, but this addon still only requires >={declared_floor} - consider bumping {keyword}."

        if args.auto_update:
            if not args.git_name or not args.git_email:
                annotations.append("::error::auto_update is enabled but git_name/git_email were not provided.")
                out.append(f"**{msg}**")
                emit(out, annotations)
                sys.exit(1)

            new_text = bump_manifest(own, keyword, args.dependency_name, actual_version)
            with open(args.manifest_file, 'w') as f:
                f.write(new_text)

            run(['git', 'config', 'user.name', args.git_name])
            run(['git', 'config', 'user.email', args.git_email])
            run(['git', 'add', args.manifest_file])
            commit_msg = f"chore: bump {keyword} floor for {args.dependency_name} to {actual_version}"
            if args.skip_ci.lower() == 'true':
                commit_msg += " [skip ci]"
            run(['git', 'commit', '-m', commit_msg])
            run(['git', 'push'])

            out.append(f"**Updated `{keyword}` for {args.dependency_name} from `{declared_floor}` to `{actual_version}` and pushed.**")
            emit(out, annotations)
            return

        out.append(f"**{msg}**")
        annotations.append(f"::error::{msg}")
        emit(out, annotations)
        sys.exit(1)

    elif declared_floor > actual_version:
        msg = f"Declared floor ({declared_floor}) is HIGHER than {args.dependency_name}'s actual published version ({actual_version}) - unusual, worth double-checking (typo, or a forward-declared requirement for an unpublished dependency version)."
        out.append(f"**{msg}**")
        annotations.append(f"::warning::{msg}")
        emit(out, annotations)

    else:
        out.append(f"Up to date - declared floor matches {args.dependency_name}'s actual current version.")
        emit(out, annotations)


def emit(report_lines, annotations):
    summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary_path:
        with open(summary_path, 'a') as f:
            f.write('\n'.join(report_lines) + '\n')
    else:
        print('\n'.join(report_lines))
    for a in annotations:
        print(a)


if __name__ == '__main__':
    main()
