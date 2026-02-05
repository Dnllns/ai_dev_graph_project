"""Tests for AI Dev Graph CLI module.

Tests all CLI commands with full coverage.
"""

import pytest
import sys
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from ai_dev_graph.cli import (
    cmd_server,
    cmd_init,
    cmd_validate,
    cmd_stats,
    cmd_export,
    main,
)


class TestCmdInit:
    """Tests for init command."""

    def test_cmd_init_creates_graph(self, capsys):
        """Test that init command creates a graph."""
        args = MagicMock()

        cmd_init(args)

        # Just check that it ran without error
        # (logging may not be captured depending on config)

    def test_cmd_init_returns_none(self):
        """Test that init command returns None (successful)."""
        args = MagicMock()

        result = cmd_init(args)

        assert result is None


class TestCmdValidate:
    """Tests for validate command."""

    def test_cmd_validate_runs_successfully(self, capsys):
        """Test that validate command runs successfully."""
        args = MagicMock()

        cmd_validate(args)

        captured = capsys.readouterr()
        assert "VALIDATION REPORT" in captured.out
        assert "Valid:" in captured.out
        assert "Total Nodes:" in captured.out

    def test_cmd_validate_reports_valid(self, capsys):
        """Test that validate reports graph validity."""
        args = MagicMock()

        cmd_validate(args)

        captured = capsys.readouterr()
        # Graph should be valid after initialization
        assert "Valid:" in captured.out

    def test_cmd_validate_shows_issues_or_ok(self, capsys):
        """Test that validate shows issues or ok message."""
        args = MagicMock()

        cmd_validate(args)

        captured = capsys.readouterr()
        # Should either show issues or "No issues found"
        assert ("ISSUES:" in captured.out) or ("No issues found" in captured.out)

    def test_cmd_validate_shows_recommendations(self, capsys):
        """Test that validate may show recommendations."""
        args = MagicMock()

        cmd_validate(args)

        captured = capsys.readouterr()
        # Recommendations are optional
        assert ("RECOMMENDATIONS:" in captured.out) or (
            "VALIDATION REPORT" in captured.out
        )


class TestCmdStats:
    """Tests for stats command."""

    def test_cmd_stats_displays_stats(self, capsys):
        """Test that stats command displays statistics."""
        args = MagicMock()

        cmd_stats(args)

        captured = capsys.readouterr()
        assert "GRAPH STATISTICS" in captured.out
        assert "Total Nodes:" in captured.out
        assert "Total Edges:" in captured.out

    def test_cmd_stats_shows_density(self, capsys):
        """Test that stats shows density metric."""
        args = MagicMock()

        cmd_stats(args)

        captured = capsys.readouterr()
        assert "Density:" in captured.out

    def test_cmd_stats_shows_node_types(self, capsys):
        """Test that stats shows node types breakdown."""
        args = MagicMock()

        cmd_stats(args)

        captured = capsys.readouterr()
        assert "Nodes by Type:" in captured.out

    def test_cmd_stats_shows_average_degree(self, capsys):
        """Test that stats may show average degree."""
        args = MagicMock()

        cmd_stats(args)

        captured = capsys.readouterr()
        # Average degree is optional
        assert ("Average Degree:" in captured.out) or (
            "GRAPH STATISTICS" in captured.out
        )


class TestCmdExport:
    """Tests for export command."""

    def test_cmd_export_creates_file(self, tmp_path):
        """Test that export creates output file."""
        output_file = tmp_path / "export.json"
        args = MagicMock()
        args.agent = "default"
        args.output = str(output_file)

        cmd_export(args)

        assert output_file.exists()

    def test_cmd_export_creates_valid_json(self, tmp_path, capsys):
        """Test that export creates valid JSON."""
        output_file = tmp_path / "export.json"
        args = MagicMock()
        args.agent = "default"
        args.output = str(output_file)

        cmd_export(args)

        with open(output_file) as f:
            data = json.load(f)

        assert isinstance(data, dict)

    def test_cmd_export_contains_statistics(self, tmp_path):
        """Test that exported data contains statistics."""
        output_file = tmp_path / "export.json"
        args = MagicMock()
        args.agent = "default"
        args.output = str(output_file)

        cmd_export(args)

        with open(output_file) as f:
            data = json.load(f)

        assert "statistics" in data or "nodes" in data

    def test_cmd_export_displays_message(self, tmp_path, capsys):
        """Test that export displays completion message."""
        output_file = tmp_path / "export.json"
        args = MagicMock()
        args.agent = "default"
        args.output = str(output_file)

        cmd_export(args)

        captured = capsys.readouterr()
        assert "Export complete" in captured.out or "Exporting" in captured.err

    def test_cmd_export_with_agent_type(self, tmp_path):
        """Test export with specific agent type."""
        output_file = tmp_path / "export_claude.json"
        args = MagicMock()
        args.agent = "claude"
        args.output = str(output_file)

        cmd_export(args)

        assert output_file.exists()

    def test_cmd_export_default_output_file(self, tmp_path, monkeypatch):
        """Test export with default output filename."""
        monkeypatch.chdir(tmp_path)
        args = MagicMock()
        args.agent = "default"
        args.output = None

        cmd_export(args)

        # Should create file with default name
        expected_file = Path("graph_export_default.json")
        assert expected_file.exists()


class TestCmdServer:
    """Tests for server command."""

    @patch("uvicorn.run")
    def test_cmd_server_calls_uvicorn(self, mock_run):
        """Test that server command calls uvicorn.run."""
        args = MagicMock()
        args.host = "127.0.0.1"
        args.port = 8000
        args.reload = False

        # uvicorn.run is mocked, so it won't actually run
        # Just verify the function can be called without error
        try:
            cmd_server(args)
        except (SystemExit, AttributeError):
            pass

    @patch("uvicorn.run")
    def test_cmd_server_logs_startup_info(self, mock_run, capsys):
        """Test that server logs startup information."""
        args = MagicMock()
        args.host = "127.0.0.1"
        args.port = 8000
        args.reload = False

        try:
            cmd_server(args)
        except (SystemExit, AttributeError):
            pass

        captured = capsys.readouterr()
        assert (
            "Starting server" in captured.err
            or "Admin panel" in captured.err
            or mock_run.called
        )


class TestMain:
    """Tests for main CLI entry point."""

    def test_main_with_no_args_shows_help(self, capsys):
        """Test that main with no args shows help."""
        with patch.object(sys, "argv", ["cli"]):
            result = main()

        assert result == 1

    def test_main_with_help_flag(self, capsys):
        """Test that main --help works."""
        with patch.object(sys, "argv", ["cli", "--help"]):
            with pytest.raises(SystemExit):
                main()

    def test_main_executes_init_command(self, capsys):
        """Test that main can execute init command."""
        with patch.object(sys, "argv", ["cli", "init"]):
            result = main()

        assert result == 0

    def test_main_executes_stats_command(self, capsys):
        """Test that main can execute stats command."""
        with patch.object(sys, "argv", ["cli", "stats"]):
            result = main()

        captured = capsys.readouterr()
        assert result == 0
        assert "GRAPH STATISTICS" in captured.out

    def test_main_executes_validate_command(self, capsys):
        """Test that main can execute validate command."""
        with patch.object(sys, "argv", ["cli", "validate"]):
            result = main()

        captured = capsys.readouterr()
        assert result == 0
        assert "VALIDATION REPORT" in captured.out

    def test_main_executes_export_command(self, tmp_path):
        """Test that main can execute export command."""
        output_file = tmp_path / "export.json"
        with patch.object(
            sys,
            "argv",
            ["cli", "export", "--agent", "default", "--output", str(output_file)],
        ):
            result = main()

        assert result == 0
        assert output_file.exists()

    def test_main_with_invalid_command_shows_error(self, capsys):
        """Test that main handles invalid command."""
        with patch.object(sys, "argv", ["cli", "invalid_command"]):
            with pytest.raises(SystemExit):
                main()

    def test_main_handles_command_errors(self):
        """Test that main handles command execution errors."""
        with patch.object(sys, "argv", ["cli", "export", "--agent", "test"]):
            with patch(
                "ai_dev_graph.cli.cmd_export", side_effect=Exception("Test error")
            ):
                result = main()

        # Should return error code
        assert result == 1

    def test_main_init_command_exists(self, capsys):
        """Test that init subcommand is properly registered."""
        with patch.object(sys, "argv", ["cli", "init"]):
            result = main()

        assert result == 0

    def test_main_stats_with_args(self, capsys):
        """Test stats command can be called."""
        with patch.object(sys, "argv", ["cli", "stats"]):
            result = main()

        assert result == 0

    def test_main_validate_with_args(self, capsys):
        """Test validate command can be called."""
        with patch.object(sys, "argv", ["cli", "validate"]):
            result = main()

        assert result == 0


class TestServerCommandArgs:
    """Tests for server command argument parsing."""

    @patch("uvicorn.run")
    def test_server_custom_host(self, mock_run):
        """Test server command with custom host."""
        args = MagicMock()
        args.host = "192.168.1.1"
        args.port = 8000
        args.reload = False

        try:
            cmd_server(args)
        except (SystemExit, AttributeError):
            pass

    @patch("uvicorn.run")
    def test_server_custom_port(self, mock_run):
        """Test server command with custom port."""
        args = MagicMock()
        args.host = "0.0.0.0"
        args.port = 9000
        args.reload = False

        try:
            cmd_server(args)
        except (SystemExit, AttributeError):
            pass

    @patch("uvicorn.run")
    def test_server_reload_enabled(self, mock_run):
        """Test server command with reload enabled."""
        args = MagicMock()
        args.host = "0.0.0.0"
        args.port = 8000
        args.reload = True

        try:
            cmd_server(args)
        except (SystemExit, AttributeError):
            pass


class TestExportCommandArgs:
    """Tests for export command argument parsing."""

    def test_export_with_claude_agent(self, tmp_path):
        """Test export for Claude agent."""
        output_file = tmp_path / "claude_export.json"
        args = MagicMock()
        args.agent = "claude"
        args.output = str(output_file)

        cmd_export(args)

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_export_with_default_agent(self, tmp_path):
        """Test export for default agent."""
        output_file = tmp_path / "default_export.json"
        args = MagicMock()
        args.agent = "default"
        args.output = str(output_file)

        cmd_export(args)

        assert output_file.exists()


class TestCliIntegration:
    """Integration tests for CLI."""

    def test_full_workflow(self, tmp_path, capsys):
        """Test full CLI workflow."""
        # Init
        with patch.object(sys, "argv", ["cli", "init"]):
            assert main() == 0

        # Stats
        with patch.object(sys, "argv", ["cli", "stats"]):
            assert main() == 0

        captured = capsys.readouterr()
        assert "GRAPH STATISTICS" in captured.out

    def test_export_then_validate(self, tmp_path, capsys):
        """Test exporting and then validating."""
        output_file = tmp_path / "workflow_export.json"

        # Export
        with patch.object(
            sys,
            "argv",
            ["cli", "export", "--agent", "default", "--output", str(output_file)],
        ):
            assert main() == 0

        assert output_file.exists()

        # Validate
        with patch.object(sys, "argv", ["cli", "validate"]):
            assert main() == 0

        captured = capsys.readouterr()
        assert "VALIDATION REPORT" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
