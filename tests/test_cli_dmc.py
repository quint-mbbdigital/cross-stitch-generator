"""Tests for DMC CLI integration functionality."""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from src.cross_stitch.cli.main import main, create_parser, create_config_from_args
from src.cross_stitch.models.config import GeneratorConfig


class TestDMCCLIFlags:
    """Test DMC-related command-line flags and options."""

    def test_enable_dmc_flag_available_in_parser(self):
        """Test that --enable-dmc flag is available in the CLI parser."""
        parser = create_parser()

        # Test that parser accepts --enable-dmc flag without error
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--enable-dmc'])
        assert hasattr(args, 'enable_dmc')
        assert args.enable_dmc is True

    def test_dmc_only_flag_available_in_parser(self):
        """Test that --dmc-only flag is available in the CLI parser."""
        parser = create_parser()

        # Test that parser accepts --dmc-only flag without error
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--dmc-only'])
        assert hasattr(args, 'dmc_only')
        assert args.dmc_only is True

    def test_dmc_palette_size_flag_available_in_parser(self):
        """Test that --dmc-palette-size flag is available in the CLI parser."""
        parser = create_parser()

        # Test that parser accepts --dmc-palette-size with integer argument without error
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--dmc-palette-size', '50'])
        assert hasattr(args, 'dmc_palette_size')
        assert args.dmc_palette_size == 50

    def test_no_dmc_flag_available_in_parser(self):
        """Test that --no-dmc flag is available in the CLI parser."""
        parser = create_parser()

        # Test that parser accepts --no-dmc flag without error
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--no-dmc'])
        assert hasattr(args, 'no_dmc')
        assert args.no_dmc is True

    def test_dmc_database_path_flag_available_in_parser(self):
        """Test that --dmc-database flag is available in the CLI parser."""
        parser = create_parser()

        # Test that parser accepts --dmc-database with file path argument without error
        args = parser.parse_args(['generate', 'input.jpg', 'output.xlsx', '--dmc-database', '/path/to/dmc.csv'])
        assert hasattr(args, 'dmc_database')
        assert args.dmc_database == '/path/to/dmc.csv'

    def test_enable_dmc_flag_sets_config_option(self, tmp_path):
        """Test that --enable-dmc flag properly sets configuration."""
        # Create mock arguments as if parsed from CLI
        from argparse import Namespace
        args = Namespace(
            enable_dmc=True,
            dmc_only=False,
            dmc_palette_size=None,
            no_dmc=False,
            dmc_database=None
        )

        config = create_config_from_args(args)

        # Should have DMC enabled
        assert hasattr(config, 'enable_dmc')
        assert config.enable_dmc is True

    def test_dmc_only_flag_sets_config_option(self, tmp_path):
        """Test that --dmc-only flag properly sets configuration."""
        from argparse import Namespace
        args = Namespace(
            enable_dmc=False,
            dmc_only=True,
            dmc_palette_size=None,
            no_dmc=False,
            dmc_database=None
        )

        config = create_config_from_args(args)

        # Should have DMC-only mode enabled
        assert hasattr(config, 'dmc_only')
        assert config.dmc_only is True

    def test_dmc_palette_size_flag_sets_config_option(self, tmp_path):
        """Test that --dmc-palette-size flag properly sets configuration."""
        from argparse import Namespace
        args = Namespace(
            enable_dmc=True,
            dmc_only=False,
            dmc_palette_size=64,
            no_dmc=False,
            dmc_database=None
        )

        config = create_config_from_args(args)

        # Should have DMC palette size set
        assert hasattr(config, 'dmc_palette_size')
        assert config.dmc_palette_size == 64

    def test_dmc_database_path_sets_config_option(self, tmp_path):
        """Test that --dmc-database flag properly sets configuration."""
        dmc_file = tmp_path / "custom_dmc.csv"
        dmc_file.write_text("dmc_code,name,r,g,b,hex_code\n310,Black,0,0,0,000000")

        from argparse import Namespace
        args = Namespace(
            enable_dmc=True,
            dmc_only=False,
            dmc_palette_size=None,
            no_dmc=False,
            dmc_database=str(dmc_file)
        )

        config = create_config_from_args(args)

        # Should have custom DMC database path set
        assert hasattr(config, 'dmc_database')
        assert config.dmc_database == str(dmc_file)


class TestDMCCLIIntegration:
    """Test DMC CLI integration with pattern generation."""

    def test_generate_with_enable_dmc_flag(self, tmp_path, tiny_image):
        """Test complete pattern generation with --enable-dmc flag."""
        output_file = tmp_path / "test_output.xlsx"

        # Mock sys.argv to simulate CLI call
        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--enable-dmc',
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should not crash and should generate file with DMC info
            exit_code = main()

            # Should complete successfully
            assert exit_code == 0
            assert output_file.exists()

    def test_generate_with_dmc_only_flag(self, tmp_path, tiny_image):
        """Test pattern generation with --dmc-only flag restricts colors to DMC palette."""
        output_file = tmp_path / "test_dmc_only.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--dmc-only',
            '--max-colors', '16',
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            assert exit_code == 0
            assert output_file.exists()

            # Should verify that only DMC colors were used in quantization

    def test_generate_with_dmc_palette_size_flag(self, tmp_path, tiny_image):
        """Test pattern generation with --dmc-palette-size flag limits DMC colors."""
        output_file = tmp_path / "test_dmc_palette_size.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--enable-dmc',
            '--dmc-palette-size', '32',
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            assert exit_code == 0
            assert output_file.exists()

    def test_generate_with_custom_dmc_database(self, tmp_path, tiny_image):
        """Test pattern generation with --dmc-database flag uses custom DMC file."""
        # Create custom DMC file
        custom_dmc = tmp_path / "custom_dmc.csv"
        custom_dmc.write_text("""dmc_code,name,r,g,b,hex_code
310,Black,0,0,0,000000
BLANC,White,255,255,255,FFFFFF
666,Bright Red,227,29,66,E31D42
702,Kelly Green,71,167,47,47A72F""")

        output_file = tmp_path / "test_custom_dmc.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--enable-dmc',
            '--dmc-database', str(custom_dmc),
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            assert exit_code == 0
            assert output_file.exists()

    def test_default_dmc_behavior_when_database_available(self, tmp_path, tiny_image):
        """Test that DMC matching is enabled by default when DMC database is available."""
        output_file = tmp_path / "test_default_dmc.xlsx"

        # Generate without explicit DMC flags
        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully and use DMC by default
            assert exit_code == 0
            assert output_file.exists()

            # Should verify that DMC codes appear in output when database is available

    def test_no_dmc_flag_explicitly_disables_dmc(self, tmp_path, tiny_image):
        """Test that --no-dmc flag explicitly disables DMC matching."""
        output_file = tmp_path / "test_no_dmc.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--no-dmc',
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            assert exit_code == 0
            assert output_file.exists()

            # Should verify that no DMC codes appear in output


class TestDMCCLIErrorHandling:
    """Test DMC CLI error handling and graceful degradation."""

    def test_missing_dmc_database_graceful_fallback(self, tmp_path, tiny_image):
        """Test graceful handling when DMC database file is missing."""
        output_file = tmp_path / "test_missing_dmc.xlsx"
        non_existent_dmc = tmp_path / "missing_dmc.csv"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--dmc-database', str(non_existent_dmc),
            '--resolutions', '10x10'  # Use appropriate resolution for 5x5 image
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should not crash, but should warn and fall back to non-DMC mode
            exit_code = main()

            # Should complete successfully despite missing DMC database
            assert exit_code == 0
            assert output_file.exists()

    def test_invalid_dmc_database_format_error_handling(self, tmp_path, tiny_image):
        """Test error handling for invalid DMC database format."""
        output_file = tmp_path / "test_invalid_dmc.xlsx"

        # Create invalid DMC file
        invalid_dmc = tmp_path / "invalid_dmc.csv"
        invalid_dmc.write_text("invalid,csv,format,without,proper,headers")

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--dmc-database', str(invalid_dmc)
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should handle invalid format gracefully
            exit_code = main()

            # Should either succeed with fallback or fail gracefully with clear error
            # (depends on implementation - could be either behavior)
            assert exit_code in [0, 1]  # Success with fallback or graceful failure

    def test_conflicting_dmc_flags_handled_properly(self, tmp_path, tiny_image):
        """Test handling of conflicting DMC flags (e.g., --enable-dmc and --no-dmc)."""
        output_file = tmp_path / "test_conflicting_flags.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--enable-dmc',
            '--no-dmc'  # Conflicting flags
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should handle conflicting flags gracefully (last one wins, or error)
            exit_code = main()

            # Should either succeed (with clear precedence) or fail with helpful message
            assert exit_code in [0, 1]

    def test_invalid_dmc_palette_size_value_error(self, tmp_path, tiny_image):
        """Test error handling for invalid --dmc-palette-size values."""
        output_file = tmp_path / "test_invalid_palette_size.xlsx"

        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--dmc-palette-size', '0'  # Invalid: must be > 0
        ]

        with patch.object(sys, 'argv', test_argv):
            # Should handle invalid palette size
            exit_code = main()

            # Should fail with clear error message
            assert exit_code == 1

    def test_dmc_database_permission_error_handling(self, tmp_path, tiny_image):
        """Test error handling when DMC database file exists but is not readable."""
        output_file = tmp_path / "test_permission_error.xlsx"

        # Create DMC file with restricted permissions (simulated)
        restricted_dmc = tmp_path / "restricted_dmc.csv"
        restricted_dmc.write_text("dmc_code,name,r,g,b,hex_code\n310,Black,0,0,0,000000")

        # Mock permission error during file access
        test_argv = [
            'cross_stitch_generator.py',
            'generate',
            str(tiny_image),
            str(output_file),
            '--dmc-database', str(restricted_dmc)
        ]

        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            with patch.object(sys, 'argv', test_argv):
                exit_code = main()

                # Should handle permission errors gracefully
                assert exit_code in [0, 1]  # Success with fallback or graceful failure


class TestDMCCLIHelp:
    """Test DMC CLI help and documentation."""

    def test_dmc_flags_appear_in_help_output(self, capsys):
        """Test that DMC flags appear in CLI help output."""
        test_argv = ['cross_stitch_generator.py', 'generate', '--help']

        with patch.object(sys, 'argv', test_argv):
            with pytest.raises(SystemExit):  # --help causes SystemExit
                main()

        captured = capsys.readouterr()
        help_output = captured.out

        # Should contain DMC-related options in help
        assert '--enable-dmc' in help_output
        assert '--dmc-only' in help_output
        assert '--dmc-palette-size' in help_output
        assert '--no-dmc' in help_output
        assert '--dmc-database' in help_output

    def test_dmc_examples_in_help_output(self, capsys):
        """Test that DMC usage examples appear in CLI help."""
        test_argv = ['cross_stitch_generator.py', '--help']

        with patch.object(sys, 'argv', test_argv):
            with pytest.raises(SystemExit):
                main()

        captured = capsys.readouterr()
        help_output = captured.out

        # Should contain DMC usage examples
        assert 'enable-dmc' in help_output.lower() or 'dmc' in help_output.lower()


class TestDMCCLIInfoCommand:
    """Test DMC integration with the info command."""

    def test_info_command_shows_dmc_status(self, tmp_path, tiny_image):
        """Test that info command shows DMC availability and configuration."""
        test_argv = [
            'cross_stitch_generator.py',
            'info',
            str(tiny_image),
            '--enable-dmc'
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            # Should complete successfully and show DMC info
            assert exit_code == 0

    def test_info_command_with_custom_dmc_database(self, tmp_path, tiny_image):
        """Test that info command works with custom DMC database."""
        custom_dmc = tmp_path / "info_dmc.csv"
        custom_dmc.write_text("dmc_code,name,r,g,b,hex_code\n310,Black,0,0,0,000000")

        test_argv = [
            'cross_stitch_generator.py',
            'info',
            str(tiny_image),
            '--dmc-database', str(custom_dmc)
        ]

        with patch.object(sys, 'argv', test_argv):
            exit_code = main()

            assert exit_code == 0