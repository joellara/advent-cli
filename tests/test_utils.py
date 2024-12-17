from mock import patch, mock_open
from _fixtures import env_patch_fixture

import os
from advent_cli import utils


def test_utils_colored_disabled():
    assert utils.colored('*', 'yellow') == '*'
    assert utils.colored('*', 'cyan') == '/'
    assert utils.colored('*', 'grey') == '.'
    assert utils.colored('text', 'red') == 'text'


@patch.dict(os.environ, {'ADVENT_DISABLE_TERMCOLOR': '0'})
@patch('advent_cli.utils.tc_colored')
def test_utils_colored_enabled(mock_tc_colored):
    _ = utils.colored('text', 'red')
    mock_tc_colored.assert_called_once_with('text', 'red')


@patch('builtins.open', mock_open(read_data='1,2,3,4\n5,6,7,8\n'))
@patch('advent_cli.utils.import_module')
def test_compute_answers(mock_import_module):
    mock_import_module.return_value.parse_input.side_effect = \
        lambda l: [[int(x) for x in line.split(',')] for line in l]
    mock_import_module.return_value.part1.side_effect = \
        lambda l: sum([x for line in l for x in line])
    mock_import_module.return_value.part2.side_effect = \
        lambda l: [x for line in l for x in line][-1]
    part1_answer, part2_answer = utils.compute_answers('2099', '99', '2099/99/example_input.txt')
    mock_import_module.assert_called_once_with('2099.99.solution')
    assert part1_answer == 36
    assert part2_answer == 8

    # test generator
    mock_import_module.return_value.parse_input.side_effect = \
        lambda l: ([int(x) for x in line.split(',')] for line in l)
    part1_answer, part2_answer = utils.compute_answers('2099', '92', '2099/92/example_input.txt')
    assert part1_answer == 36
    assert part2_answer == 8


@patch('requests.post')
def test_submit_answer_pass(mock_post):
    mock_post.return_value.text = "That's the right answer"
    assert utils.submit_answer('2099', '99', '1', '5') == (utils.Status.PASS, None)


@patch('requests.post')
def test_submit_answer_fail(mock_post):
    mock_post.return_value.text = "That's not the right answer"
    assert utils.submit_answer('2099', '99', '1', '5') == (utils.Status.FAIL, None)


@patch('requests.post')
def test_submit_answer_ratelimit(mock_post):
    mock_post.return_value.text = 'You gave an answer too recently'
    assert utils.submit_answer('2099', '99', '1', '5') == (utils.Status.RATE_LIMIT, None)


@patch('requests.post')
def test_submit_answer_completed(mock_post):
    mock_post.return_value.text = 'Did you already complete it?'
    assert utils.submit_answer('2099', '99', '1', '5') == (utils.Status.COMPLETED, None)


@patch('requests.post')
def test_submit_answer_unknown_response(mock_post):
    mock_post.return_value.text = 'Error'
    assert utils.submit_answer('2099', '99', '1', '5') == (utils.Status.UNKNOWN, 'Error')


def test_custom_markdown():
    html = ('<pre><code>this is <em>emphasized</em> text</code></pre>'
            'this is <em>not</em> in a code block')
    with patch.dict(os.environ, {'ADVENT_MARKDOWN_EM': 'default'}):
        assert utils.custom_markdownify(html) == ('\n```\nthis is *emphasized* text'
                                                  '\n```\nthis is *not* in a code block')
    with patch.dict(os.environ, {'ADVENT_MARKDOWN_EM': 'none'}):
        assert utils.custom_markdownify(html) == ('\n```\nthis is emphasized text'
                                                  '\n```\nthis is *not* in a code block')
    with patch.dict(os.environ, {'ADVENT_MARKDOWN_EM': 'ib'}):
        assert utils.custom_markdownify(html) == ('\n<pre><code>this is '
                                                  '<i><b>emphasized</b></i> '
                                                  'text</code></pre>\n'
                                                  'this is *not* in a code block')
    with patch.dict(os.environ, {'ADVENT_MARKDOWN_EM': 'mark'}):
        assert utils.custom_markdownify(html) == ('\n<pre><code>this is '
                                                  '<mark>emphasized</mark> '
                                                  'text</code></pre>\n'
                                                  'this is *not* in a code block')
