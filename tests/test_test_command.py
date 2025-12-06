from mock import patch
from _fixtures import env_patch_fixture

from advent_cli import commands


@patch("advent_cli.commands.compute_answers", return_value=(None, None))
@patch("os.path.exists", return_value=True)
@patch("os.getcwd", return_value="/fake/path")
def test_test_no_solution(mock_getcwd, mock_exists, mock_compute, capsys):
    commands.test("2099", "99")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Using input file: /fake/path/2099/99/input.txt\nNo solution implemented\n"
    )


@patch("advent_cli.commands.compute_answers", return_value=(5, None))
@patch("os.path.exists", return_value=True)
@patch("os.getcwd", return_value="/fake/path")
def test_test_part1(mock_getcwd, mock_exists, mock_compute, capsys):
    commands.test("2099", "99")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == ("Using input file: /fake/path/2099/99/input.txt\nPart 1: 5\n")


@patch("advent_cli.commands.compute_answers", return_value=(5, None))
@patch("os.path.exists", return_value=True)
@patch("os.getcwd", return_value="/fake/path")
def test_test_part1_altsoln(mock_getcwd, mock_exists, mock_compute, capsys):
    commands.test("2099", "99", solution_file="solution2")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Using input file: "
        "/fake/path/2099/99/input.txt\n"
        "(Using solution2.py)\n"
        "Part 1: 5\n"
        "Output matches solution.py\n"
    )


@patch("os.getcwd", return_value="/fake/path")
@patch("os.path.exists", side_effect=[True, False])
def test_test_part1_altsoln_nofile(mock_exists, mock_getcwd, capsys):
    commands.test("2099", "99", solution_file="solution2")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Using input file: /fake/path/2099/99/input.txt\n"
        "Solution file does not exist:\n"
        '  "/fake/path/2099/99/solution2.py"\n'
    )


@patch("advent_cli.commands.compute_answers", side_effect=[(2, None), (5, None)])
@patch("os.path.exists", return_value=True)
@patch("os.getcwd", return_value="/fake/path")
def test_test_part1_wrong(mock_getcwd, mock_exists, mock_compute, capsys):
    commands.test("2099", "99", solution_file="solution2")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Using input file: "
        "/fake/path/2099/99/input.txt\n"
        "(Using solution2.py)\n"
        "Part 1: 2\n"
        "Output does not match solution.py\n"
    )


@patch("advent_cli.commands.compute_answers", return_value=(5, None))
@patch("os.stat")
@patch("os.path.exists", return_value=True)
def test_test_part1_example(mock_exists, mock_stat, mock_compute, capsys):
    mock_stat.return_value.st_size = 1
    with patch("os.getcwd", return_value="/fake/path"):
        commands.test("2099", "99", input_file="example_input.txt")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Using input file: /fake/path/2099/99/example_input.txt\nPart 1: 5\n"
    )


@patch("advent_cli.commands.compute_answers", return_value=(5, None))
@patch("os.getcwd", return_value="/fake/path")
@patch("os.stat")
@patch("os.path.exists", return_value=True)
def test_test_part1_example_empty(mock_exists, mock_stat, mock_getcwd, mock_compute, capsys):
    mock_stat.return_value.st_size = 0

    # simulate missing example file
    def _exists(path):
        return not path.endswith("example_input.txt")

    with patch("os.getcwd", return_value="/fake/path"):
        with patch("os.path.exists", side_effect=_exists):
            commands.test("2099", "99", input_file="example_input.txt")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Example input file does not exist:\n"
        "  /fake/path/2099/99/example_input.txt\n"
        "Using input file: example_input.txt\n"
        "Part 1: 5\n"
    )


@patch("advent_cli.commands.compute_answers", return_value=(5, 10))
@patch("os.path.exists", return_value=True)
@patch("os.getcwd", return_value="/fake/path")
def test_test_part1_part2(mock_getcwd, mock_exists, mock_compute, capsys):
    commands.test("2099", "99")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == (
        "Using input file: /fake/path/2099/99/input.txt\nPart 1: 5\nPart 2: 10\n"
    )


@patch("os.getcwd", return_value="/fake/path")
@patch("os.path.exists", return_value=False)
def test_test_no_dir(mock_exists, mock_getcwd, capsys):
    commands.test("2099", "99")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == ('Directory does not exist:\n  "/fake/path/2099/99/"\n')
