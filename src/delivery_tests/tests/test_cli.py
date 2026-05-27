"""
test_cli.py
===========
Pure unit tests for the delivery-cli command-line interface. Uses
Click's `CliRunner` to invoke commands without actually requiring a
ROS master - we monkey-patch the rospy imports inside the CLI so the
test focuses on argument parsing, help text, and the bag subcommands
that do not need ROS.

Scenarios:
    1. `--help` exits cleanly with the expected text.
    2. `--version` prints 1.0.0.
    3. `bag list` on an empty directory prints a friendly message.
    4. `bag list` on a directory with .bag files lists them.
"""

import os
import sys

import pytest
from click.testing import CliRunner

# Add the CLI package to the path so `from delivery_cli.main import cli`
# works without an editable install.
HERE = os.path.dirname(__file__)
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "src", "delivery_cli"))

from delivery_cli.main import cli  # noqa: E402


@pytest.fixture
def runner():
    return CliRunner()


def test_help(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Campus Delivery Robot" in result.output
    # Each subcommand should appear in the top-level help.
    for sub in ("deliver", "stop", "resume", "box", "say",
                "status", "watch", "bag", "list-destinations"):
        assert sub in result.output


def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_bag_help(runner):
    result = runner.invoke(cli, ["bag", "--help"])
    assert result.exit_code == 0
    assert "start" in result.output
    assert "stop" in result.output
    assert "list" in result.output


def test_bag_list_empty(tmp_path, runner):
    result = runner.invoke(cli, ["bag", "list", "-o", str(tmp_path)])
    assert result.exit_code == 0
    assert "no .bag files" in result.output


def test_bag_list_with_files(tmp_path, runner):
    # Drop a fake bag file in the directory.
    fake = tmp_path / "demo.bag"
    fake.write_bytes(b"x" * 1024 * 1024)  # 1 MB
    result = runner.invoke(cli, ["bag", "list", "-o", str(tmp_path)])
    assert result.exit_code == 0
    assert "demo.bag" in result.output


def test_box_help(runner):
    result = runner.invoke(cli, ["box", "--help"])
    assert result.exit_code == 0
    assert "open" in result.output
    assert "close" in result.output


def test_deliver_help(runner):
    result = runner.invoke(cli, ["deliver", "--help"])
    assert result.exit_code == 0
    assert "DESTINATION" in result.output
    assert "--wait" in result.output
    assert "--timeout" in result.output
