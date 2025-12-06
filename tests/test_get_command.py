from mock import patch, call, mock_open, MagicMock
from _fixtures import env_patch_fixture

from advent_cli import commands


@patch("os.makedirs")
@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
def test_get(mock_get, mock_open, mock_mkdir):
    mock_get.side_effect = [
        MagicMock(
            text="""
            <meta charset="utf-8">
            <article class="day-desc">
                <h2>--- Day 1: Test ---</h2>
                <p>This is a test puzzle.</p>
            </article>
        """
        ),
        MagicMock(text="0,1,2,3,4"),
    ]
    commands.get("2099", "99")
    mock_open.assert_has_calls(
        [
            call("2099/99/prompt.md", "w"),
            call("2099/99/input.txt", "w"),
            call("2099/99/example_input.txt", "w"),
            call("2099/99/solution.py", "w"),
        ],
        any_order=True,
    )
    mock_open.assert_has_calls(
        [
            call()
            .__enter__()
            .write("\n\nDay 1: Test\n-----------\n\nThis is a test puzzle.\n\n"),
            call().__enter__().write("0,1,2,3,4"),
            call()
            .__enter__()
            .write(
                (
                    "## Advent of Code 2099\n"
                    "## https://adventofcode.com/2099/day/99\n"
                    "## --- Day 1: Test ---\n\n"
                    "import os\n\n"
                    "def parse_input(lines: list[str]):\n"
                    "    pass\n\n"
                    "def part1(data):\n"
                    "    pass\n\n"
                    "def part2(data):\n"
                    "    pass\n\n"
                    'if __name__ == "__main__":\n'
                    "    current_dir = os.path.dirname(os.path.abspath(__file__))\n"
                    '    with open(os.path.join(current_dir, "example_input.txt"), "r") as f:\n'
                    "        lines = f.readlines()\n"
                    "    data = parse_input(lines)\n"
                    "    print(part1(data))\n"
                    "    print(part2(data))"
                )
            ),
        ],
        any_order=True,
    )
    mock_mkdir.assert_called_once_with("2099/99/")


@patch("builtins.open", new_callable=mock_open())
@patch("os.path.exists")
def test_get_path_exists(mock_exists, mock_open):
    mock_exists.side_effect = lambda x: {"2099/99/": True}[x]
    commands.get("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
def test_get_puzzle_locked(mock_get, mock_open):
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = (
        "Please don't repeatedly request this endpoint before it unlocks!"
    )
    commands.get("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
def test_get_404(mock_get, mock_open):
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = "404 Not Found"
    commands.get("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
@patch("os.path.exists", return_value=True)
def test_refresh_prompt(mock_exists, mock_get, mock_open):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = """
        <meta charset="utf-8">
        <article class="day-desc">
            <h2>--- Day 1: Test ---</h2>
            <p>This is a test puzzle.</p>
        </article>
    """
    commands.refresh_prompt("2099", "99")
    mock_open.assert_has_calls(
        [
            call("2099/99/prompt.md", "w"),
        ],
        any_order=True,
    )
    mock_open.assert_has_calls(
        [
            call()
            .__enter__()
            .write("\n\nDay 1: Test\n-----------\n\nThis is a test puzzle.\n\n"),
        ],
        any_order=True,
    )


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
@patch("os.path.exists", return_value=True)
def test_refresh_prompt_with_part2(mock_exists, mock_get, mock_open):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = """
        <meta charset="utf-8">
        <article class="day-desc">
            <h2>--- Day 1: Test ---</h2>
            <p>This is part 1.</p>
        </article>
        <article class="day-desc">
            <h2>--- Part Two ---</h2>
            <p>This is part 2.</p>
        </article>
    """
    commands.refresh_prompt("2099", "99")
    mock_open.assert_has_calls(
        [
            call("2099/99/prompt.md", "w"),
        ],
        any_order=True,
    )
    mock_open.assert_has_calls(
        [
            call().__enter__().write("\n\nDay 1: Test\n-----------\n\nThis is part 1.\n\n"),
            call().__enter__().write("\n\nPart Two\n--------\n\nThis is part 2.\n\n"),
        ],
        any_order=True,
    )


@patch("builtins.open", new_callable=mock_open())
@patch("os.path.exists")
def test_refresh_prompt_path_not_exists(mock_exists, mock_open):
    mock_exists.return_value = False
    commands.refresh_prompt("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
@patch("os.path.exists", return_value=True)
def test_refresh_prompt_locked(mock_exists, mock_get, mock_open):
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = (
        "Please don't repeatedly request this endpoint before it unlocks!"
    )
    commands.refresh_prompt("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
@patch("os.path.exists", return_value=True)
def test_refresh_prompt_404(mock_exists, mock_get, mock_open):
    mock_get.return_value.status_code = 404
    mock_get.return_value.text = "404 Not Found"
    commands.refresh_prompt("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
@patch("os.path.exists", return_value=True)
def test_refresh_prompt_not_logged_in(mock_exists, mock_get, mock_open):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "[Log In]"
    commands.refresh_prompt("2099", "99")
    mock_open.assert_not_called()


@patch("builtins.open", new_callable=mock_open())
@patch("requests.get")
@patch("os.path.exists", return_value=True)
def test_refresh_prompt_no_prompt(mock_exists, mock_get, mock_open, capsys):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = '<meta charset="utf-8"></meta>'
    commands.refresh_prompt("2099", "99")
    captured_stdout = capsys.readouterr().out
    assert captured_stdout == "No prompt found on the page.\n"
    mock_open.assert_not_called()
