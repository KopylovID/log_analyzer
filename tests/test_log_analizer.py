import pytest
from pathlib import Path
from unittest.mock import Mock
from src.app.log_analyzer import LogAnalizer
from tempfile import NamedTemporaryFile

class TestLogAnalizer:

    @pytest.fixture
    def log_analizer(self):
        config = Mock()
        logger = Mock()
        return LogAnalizer(config, logger)

    @pytest.fixture
    def temp_file(self, request):
        data = request.param
        with NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write(data)
            path = Path(f.name)

        yield path
        path.unlink()

    @pytest.mark.parametrize('temp_file,expected', [
        ("line1\nline2", 2),
        ("line1\nline2\nline3\nline4", 4),
        ("", 0)
    ], indirect=['temp_file'])
    def test_count_lines(self, log_analizer, temp_file, expected):
        result = log_analizer._count_lines(temp_file)
        assert result == expected

    @pytest.mark.parametrize('value,expected', [
        ("3.98", 3.98),
        ("4.54", 4.54),
        ("qwe", 0.00)
    ])
    def test_try_cast_to_float(self, log_analizer, value, expected):
        result = log_analizer._try_cast_to_float(value)
        assert result == expected
