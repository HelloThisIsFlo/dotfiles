from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = next(
    path
    for path in (
        SCRIPT_DIR / "executable_collect_project_evidence.py",
        SCRIPT_DIR / "collect_project_evidence.py",
    )
    if path.is_file()
)
SPEC = importlib.util.spec_from_file_location(
    "reconstruct_project_evidence",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
collector = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = collector
SPEC.loader.exec_module(collector)


def run_git(root: Path, *args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


class DayWindowTests(unittest.TestCase):
    def test_local_day_respects_dst_transition(self):
        window = collector.build_day_window("2026-03-29", "Europe/London")
        duration = (
            window.end.astimezone(dt.timezone.utc)
            - window.start.astimezone(dt.timezone.utc)
        )

        self.assertEqual(duration, dt.timedelta(hours=23))
        self.assertEqual(window.start.isoformat(), "2026-03-29T00:00:00+00:00")
        self.assertEqual(window.end.isoformat(), "2026-03-30T00:00:00+01:00")


class RootSafetyTests(unittest.TestCase):
    def test_rejects_broad_and_credential_roots(self):
        home = Path.home().resolve()

        self.assertIsNotNone(collector.unsafe_root_reason(home, home))
        self.assertIsNotNone(collector.unsafe_root_reason(home / ".ssh", home))
        self.assertIsNotNone(
            collector.unsafe_root_reason(home / "Documents", home)
        )
        self.assertIsNone(
            collector.unsafe_root_reason(
                home / "Documents" / "Codex" / "specific-task",
                home,
            )
        )
        self.assertIsNotNone(collector.unsafe_root_reason(Path("/usr"), home))
        self.assertIsNotNone(collector.unsafe_root_reason(Path("/dev"), home))
        self.assertIsNotNone(
            collector.unsafe_root_reason(home / ".cache" / "tool", home)
        )

    def test_git_environment_cannot_redirect_requested_root(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            sandbox = Path(directory)
            requested = sandbox / "requested"
            redirected = sandbox / "redirected"
            requested.mkdir()
            redirected.mkdir()
            run_git(requested, "init", "--quiet")
            run_git(redirected, "init", "--quiet")

            with patch.dict(
                os.environ,
                {
                    "GIT_DIR": str(redirected / ".git"),
                    "GIT_WORK_TREE": str(redirected),
                },
            ):
                accepted, skipped = collector.prepare_roots(
                    [str(requested)],
                    max_roots=1,
                    timeout=2,
                )

        self.assertEqual(skipped, [])
        self.assertEqual(accepted[0]["resolved_root"], str(requested))

    def test_gitfile_cannot_redirect_outside_requested_root(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            sandbox = Path(directory)
            requested = sandbox / "requested"
            redirected = sandbox / "redirected"
            requested.mkdir()
            redirected.mkdir()
            run_git(redirected, "init", "--quiet")
            run_git(
                redirected,
                "config",
                "core.worktree",
                str(redirected),
            )
            (requested / ".git").write_text(
                f"gitdir: {redirected / '.git'}\n",
                encoding="utf-8",
            )

            accepted, skipped = collector.prepare_roots(
                [str(requested)],
                max_roots=1,
                timeout=2,
            )

        self.assertEqual(accepted, [])
        self.assertEqual(len(skipped), 1)
        self.assertIn("does not contain", skipped[0]["reason"])


class GitEvidenceTests(unittest.TestCase):
    def test_commit_order_uses_instants_across_fall_back_hour(self):
        output = (
            "aaaaaaaa\x1f2026-10-25T01:45:00+01:00"
            "\x1f2026-10-25T01:45:00+01:00\x1fEarlier instant\x1e\n"
            "bbbbbbbb\x1f2026-10-25T01:30:00+00:00"
            "\x1f2026-10-25T01:30:00+00:00\x1fLater instant\x1e\n"
        )
        command_result = {
            "state": "ok",
            "exit_code": 0,
            "duration_ms": 1,
            "stdout": output,
            "error": "",
        }

        with patch.object(
            collector,
            "run_command",
            return_value=command_result,
        ) as mocked:
            commits, truncated, errors = collector.collect_commits(
                Path("/safe/project"),
                collector.build_day_window("2026-10-25", "Europe/London"),
                max_commits=10,
                timeout=2,
            )

        command = mocked.call_args.args[0]
        self.assertIn(
            "--since-as-filter=2026-10-25T00:00:00+01:00",
            command,
        )
        self.assertFalse(truncated)
        self.assertEqual(errors, [])
        self.assertEqual(
            [commit["subject"] for commit in commits],
            ["Earlier instant", "Later instant"],
        )

    def test_collects_target_day_commit_and_current_dirty_mtime(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            root = Path(directory)
            run_git(root, "init", "--quiet")
            run_git(root, "config", "user.name", "Evidence Test")
            run_git(root, "config", "user.email", "evidence@example.invalid")

            tracked = root / "tracked.txt"
            tracked.write_text("first\n", encoding="utf-8")
            run_git(root, "add", "tracked.txt")
            commit_environment = os.environ.copy()
            commit_environment["GIT_AUTHOR_DATE"] = "2026-07-27T10:00:00+01:00"
            commit_environment["GIT_COMMITTER_DATE"] = "2026-07-27T10:00:00+01:00"
            run_git(root, "commit", "--quiet", "-m", "Target day outcome", env=commit_environment)

            tracked.write_text("changed\n", encoding="utf-8")
            dirty_time = dt.datetime(
                2026,
                7,
                27,
                11,
                tzinfo=collector.ZoneInfo("Europe/London"),
            ).timestamp()
            os.utime(tracked, (dirty_time, dirty_time))

            result = collector.collect_git_root(
                {
                    "requested_root": str(root),
                    "resolved_root": str(root),
                    "kind": "git",
                },
                collector.build_day_window("2026-07-27", "Europe/London"),
                max_commits=10,
                max_files=10,
                timeout=5,
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            [commit["subject"] for commit in result["commits"]],
            ["Target day outcome"],
        )
        self.assertEqual(
            [entry["path"] for entry in result["working_tree_files"]],
            ["tracked.txt"],
        )
        self.assertIn(
            "not attention",
            result["commits"][0]["evidence_scope"],
        )

    def test_disables_configured_fsmonitor_hook(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            root = Path(directory)
            run_git(root, "init", "--quiet")
            run_git(root, "config", "user.name", "Evidence Test")
            run_git(root, "config", "user.email", "evidence@example.invalid")

            tracked = root / "tracked.txt"
            tracked.write_text("first\n", encoding="utf-8")
            run_git(root, "add", "tracked.txt")
            run_git(root, "commit", "--quiet", "-m", "Initial state")

            marker = root / "fsmonitor-ran"
            hook = root / "fsmonitor.py"
            hook.write_text(
                "#!/usr/bin/env python3\n"
                "from pathlib import Path\n"
                f"Path({str(marker)!r}).touch()\n",
                encoding="utf-8",
            )
            hook.chmod(0o755)
            run_git(root, "config", "core.fsmonitor", str(hook))
            tracked.write_text("changed\n", encoding="utf-8")

            files, _, errors = collector.collect_dirty_files(
                root,
                collector.build_day_window(
                    dt.datetime.now(
                        collector.ZoneInfo("Europe/London")
                    ).date(),
                    "Europe/London",
                ),
                max_files=10,
                timeout=5,
            )

            self.assertEqual(errors, [])
            self.assertFalse(marker.exists())
            self.assertIn("tracked.txt", [entry["path"] for entry in files])

    def test_does_not_execute_clean_filter_or_read_worktree_content(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            root = Path(directory)
            run_git(root, "init", "--quiet")
            run_git(root, "config", "user.name", "Evidence Test")
            run_git(root, "config", "user.email", "evidence@example.invalid")

            tracked = root / "tracked.txt"
            tracked.write_text("first\n", encoding="utf-8")
            (root / ".gitattributes").write_text(
                "tracked.txt filter=evil\n",
                encoding="utf-8",
            )
            run_git(root, "add", "tracked.txt", ".gitattributes")
            run_git(root, "commit", "--quiet", "-m", "Filtered file")

            marker = root / "clean-filter-ran"
            filter_script = root / "clean_filter.py"
            filter_script.write_text(
                "#!/usr/bin/env python3\n"
                "from pathlib import Path\n"
                "import sys\n"
                f"Path({str(marker)!r}).touch()\n"
                "sys.stdout.buffer.write(sys.stdin.buffer.read())\n",
                encoding="utf-8",
            )
            filter_script.chmod(0o755)
            run_git(
                root,
                "config",
                "filter.evil.clean",
                str(filter_script),
            )
            tracked.write_text("changed secret content\n", encoding="utf-8")

            paths, errors = collector.git_path_sets(root, timeout=5)

            self.assertEqual(errors, [])
            self.assertFalse(marker.exists())
            self.assertEqual(paths["tracked.txt"], {"tracked"})

    def test_does_not_follow_symlinked_intermediate_directory(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            sandbox = Path(directory)
            root = sandbox / "repo"
            root.mkdir()
            outside = sandbox / "outside"
            outside.mkdir()
            run_git(root, "init", "--quiet")
            run_git(root, "config", "user.name", "Evidence Test")
            run_git(root, "config", "user.email", "evidence@example.invalid")

            tracked_directory = root / "dir"
            tracked_directory.mkdir()
            tracked = tracked_directory / "file.txt"
            tracked.write_text("inside\n", encoding="utf-8")
            run_git(root, "add", "dir/file.txt")
            run_git(root, "commit", "--quiet", "-m", "Track nested file")

            tracked.unlink()
            tracked_directory.rmdir()
            outside_file = outside / "file.txt"
            outside_file.write_text("outside\n", encoding="utf-8")
            tracked_directory.symlink_to(outside, target_is_directory=True)

            files, _, errors = collector.collect_dirty_files(
                root,
                collector.build_day_window(
                    dt.datetime.now(
                        collector.ZoneInfo("Europe/London")
                    ).date(),
                    "Europe/London",
                ),
                max_files=10,
                timeout=5,
            )

        self.assertEqual(errors, [])
        self.assertNotIn("dir/file.txt", [entry["path"] for entry in files])


class FilesystemEvidenceTests(unittest.TestCase):
    def test_prunes_dependencies_and_reads_only_metadata(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            root = Path(directory)
            note = root / "notes.md"
            note.write_text("remembered work\n", encoding="utf-8")
            dependency = root / "node_modules"
            dependency.mkdir()
            noise = dependency / "generated.js"
            noise.write_text("generated\n", encoding="utf-8")

            observed = dt.datetime(
                2026,
                7,
                27,
                12,
                tzinfo=collector.ZoneInfo("Europe/London"),
            ).timestamp()
            os.utime(note, (observed, observed))
            os.utime(noise, (observed, observed))

            result = collector.collect_filesystem_root(
                {
                    "requested_root": str(root),
                    "resolved_root": str(root),
                    "kind": "filesystem",
                },
                collector.build_day_window("2026-07-27", "Europe/London"),
                max_files=10,
                max_visited=100,
                max_depth=4,
                timeout=5,
            )

        self.assertEqual(result["status"], "ok")
        self.assertEqual([entry["path"] for entry in result["files"]], ["notes.md"])

    def test_empty_directory_tree_obeys_entry_limit(self):
        with tempfile.TemporaryDirectory(dir=str(Path.cwd())) as directory:
            root = Path(directory)
            for index in range(20):
                (root / f"directory-{index}").mkdir()

            result = collector.collect_filesystem_root(
                {
                    "requested_root": str(root),
                    "resolved_root": str(root),
                    "kind": "filesystem",
                },
                collector.build_day_window("2026-07-27", "Europe/London"),
                max_files=10,
                max_visited=1,
                max_depth=4,
                timeout=5,
            )

        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["entries_visited"], 1)
        self.assertIn("entry visit limit", result["stop_reason"])


class OutputContractTests(unittest.TestCase):
    def test_command_environment_disables_lazy_fetch(self):
        result = collector.run_command(
            [
                sys.executable,
                "-c",
                (
                    "import os; "
                    "print(os.environ.get('GIT_NO_LAZY_FETCH')); "
                    "print(os.environ.get('GIT_PROTOCOL_FROM_USER'))"
                ),
            ],
            timeout=2,
        )

        self.assertEqual(result["state"], "ok")
        self.assertEqual(result["stdout"].splitlines(), ["1", "0"])

    def test_command_output_has_a_hard_limit(self):
        result = collector.run_command(
            [
                sys.executable,
                "-c",
                "import sys; sys.stdout.write('x' * 10000)",
            ],
            timeout=2,
            max_output_bytes=100,
        )

        self.assertEqual(result["state"], "limit")
        self.assertEqual(result["stdout"], "")
        self.assertIn("output limit", result["error"])

    def test_emits_single_json_line_and_matching_sentinel(self):
        payload = {
            "schema_version": 1,
            "source_status": "ok",
            "roots": [],
        }
        output = io.StringIO()

        with contextlib.redirect_stdout(output):
            collector.emit(payload)

        lines = output.getvalue().splitlines()
        expected_digest = hashlib.sha256(lines[0].encode("utf-8")).hexdigest()

        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0]), payload)
        self.assertEqual(
            lines[1],
            f"RECONSTRUCT_LOCAL_EVIDENCE_COMPLETE sha256={expected_digest}",
        )

    def test_collect_reports_unavailable_when_all_roots_are_unsafe(self):
        args = argparse.Namespace(
            date="2026-07-27",
            timezone="Europe/London",
            root=[str(Path.home())],
            max_roots=12,
            max_commits=10,
            max_files=10,
            max_visited=100,
            max_depth=4,
            timeout_seconds=2,
        )

        payload = collector.collect(args)

        self.assertEqual(payload["source_status"], "unavailable")
        self.assertEqual(payload["summary"]["accepted_roots"], 0)
        self.assertEqual(payload["summary"]["skipped_roots"], 1)


if __name__ == "__main__":
    unittest.main()
