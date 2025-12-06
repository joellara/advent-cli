from freezegun import freeze_time
from mock import patch
from _fixtures import env_patch_fixture

from advent_cli import commands


@freeze_time("2099-12-03")
@patch("curses.wrapper")
def test_countdown_input(mock_wrapper):
    commands.countdown("2099", "02")
    commands.countdown("2100", "04")
    mock_wrapper.assert_not_called()


@freeze_time("2099-12-05")
@patch("curses.wrapper")
def test_countdown_already_unlocked(mock_wrapper, capsys):
    commands.countdown("2099", "03")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == "That puzzle has already been unlocked.\n"
    mock_wrapper.assert_not_called()
