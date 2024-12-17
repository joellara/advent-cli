import curses
import os
import pytz
import re
import requests
import sys
import time

from bs4 import BeautifulSoup
from datetime import datetime as dt
from tabulate import tabulate
from jinja2 import Template

from . import config
from .utils import (
    colored,
    compute_answers,
    custom_markdownify,
    get_time_until_unlock,
    submit_answer,
    Status
)

INPUT_FILE_NAME = "input.txt"

def get_solution(year, day):
    if not os.path.exists(f'{year}/{day}/'):
        print(colored('Directory does not exist, first get the puzzle:', 'red'))
        print(colored(f'  {os.getcwd()}/{year}/{day}/', 'red'))
        return

    conf = config.get_config()
    r = requests.get(f'https://adventofcode.com/{year}/day/{int(day)}',
                     cookies={'session': conf['session_cookie']})
    if r.status_code == 404:
        if 'before it unlocks!' in r.text:
            print(colored('This puzzle has not unlocked yet.', 'red'))
            print(colored(f'It will unlock on Dec {day} {year} at midnight EST (UTC-5).',
                          'red'))
            print(colored(f'Use "advent countdown {year}/{day}" to view a live countdown.',
                          'grey'))
            return
        else:
            print(colored('The server returned error 404 for url:', 'red'))
            print(colored(f'  "https://adventofcode.com/{year}/day/{int(day)}/"', 'red'))
            return
    elif '[Log In]' in r.text:
        print(colored('Session cookie is invalid or expired.', 'red'))
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    def find_solutions(element):
        if element.name == 'p' and re.search(r'Your puzzle answer was', element.text):
            return True
        return False
    solutions = soup.find_all(find_solutions)

    print(solutions)
    if len(solutions) == 0:
        print(colored('No solutions found.', 'red'))
        return

    number = 1
    for solution in solutions:
        answer = solution.find('code').text
        # write a file named solution1.txt with the answer
        with open(f'{year}/{day}/solution{number}.txt', 'w') as f:
            f.write(answer)
        print(f'Wrote solution to {year}/{day}/solution{number}.txt')
        number += 1
    
    print(colored('All solutions written.', 'green'))

def get_puzzle_day(year, day):
    if os.path.exists(f'{year}/{day}/'):
        print(colored('Directory already exists:', 'red'))
        print(colored(f'  {os.getcwd()}/{year}/{day}/', 'red'))
        return

    conf = config.get_config()
    r = requests.get(f'https://adventofcode.com/{year}/day/{int(day)}',
                     cookies={'session': conf['session_cookie']})
    if r.status_code == 404:
        if 'before it unlocks!' in r.text:
            print(colored('This puzzle has not unlocked yet.', 'red'))
            print(colored(f'It will unlock on Dec {day} {year} at midnight EST (UTC-5).',
                          'red'))
            print(colored(f'Use "advent countdown {year}/{day}" to view a live countdown.',
                          'grey'))
            return
        else:
            print(colored('The server returned error 404 for url:', 'red'))
            print(colored(f'  "https://adventofcode.com/{year}/day/{int(day)}/"', 'red'))
            return
    elif '[Log In]' in r.text:
        print(colored('Session cookie is invalid or expired.', 'red'))
        return

    os.makedirs(f'{year}/{day}/')

    soup = BeautifulSoup(r.text, 'html.parser')
    parts = soup.find_all('article', class_='day-desc')

    part1_html = parts[0].decode_contents()

    title = parts[0].find('h2').text
    # remove hyphens from title sections, makes markdown look nicer
    part1_html = re.sub('--- (.*) ---', r'\1', part1_html)

    # also makes markdown look better
    part1_html = part1_html.replace('\n\n', '\n')

    with open(f'{year}/{day}/prompt.md', 'w') as f:
        f.write(custom_markdownify(part1_html))
        if len(parts) == 2:
            part2_html = parts[1].decode_contents()
            f.write(custom_markdownify(part2_html))
    print(f'Downloaded prompt to {year}/{day}/prompt.md')

    r = requests.get(f'https://adventofcode.com/{year}/day/{int(day)}/input',
                     cookies={'session': conf['session_cookie']})
    with open(f'{year}/{day}/{INPUT_FILE_NAME}', 'w') as f:
        f.write(r.text)
    print(f'Downloaded input to {year}/{day}/{INPUT_FILE_NAME}')

    open(f'{year}/{day}/example_input.txt', 'w').close()
    print(f'Created {year}/{day}/example_input.txt')

    template = Template("""## Advent of Code {{ year }}
## https://adventofcode.com/{{ year }}/day/{{ day }}
## {{ title }}

import os

def parse_input(lines: list[str]):
    pass

def part1(data):
    pass

def part2(data):
    pass

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "example_input.txt"), "r") as f:
        lines = f.readlines()
    data = parse_input(lines)
    print(part1(data))
    print(part2(data))
""")

    with open(f'{year}/{day}/solution.py', 'w') as f:
        f.write(template.render(year=year, day=day, title=title))
    print(f'Created {year}/{day}/solution.py')

def get(year, day):
    if day is None:
        curr_date = dt.now(pytz.timezone('America/New_York'))
        if year < curr_date.year:
            for day in range(1, 26):
                get_puzzle_day(year, day)
        else:
            for day in range(1, curr_date.day + 1):
                get_puzzle_day(year, day)
    else:
        get_puzzle_day(year, day)

def stats(year):
    today = dt.today()
    if today.year <= int(year) and today.month < 12:
        print(colored(f'Defaulting to previous year ({today.year - 1}).', 'red'))
        year = str(today.year - 1)

    conf = config.get_config()
    r = requests.get(f'https://adventofcode.com/{year}/leaderboard/self',
                     cookies={'session': conf['session_cookie']})
    if '[Log In]' in r.text:
        print(colored('Session cookie is invalid or expired.', 'red'))
        return

    soup = BeautifulSoup(r.text, 'html.parser')

    table = soup.select('article pre')[0].text
    table_rows = [x.split() for x in table.split('\n')[2:-1]]

    stars_per_day = [0] * 25
    for row in table_rows:
        stars_per_day[int(row[0]) - 1] = 2 if row[4:7] != ['-', '-', '-'] \
                                           else 1 if row[1:4] != ['-', '-', '-'] \
                                           else 0

    print('\n         1111111111222222\n1234567890123456789012345')

    today = dt.now(pytz.timezone('America/New_York'))
    for i, stars in enumerate(stars_per_day):
        if stars == 2:
            print(colored('*', 'yellow'), end='')
        elif stars == 1:
            print(colored('*', 'cyan'), end='')
        elif stars == 0 and today.year == int(year) and today.day < (i + 1):
            print(' ', end='')
        else:
            print(colored('*', 'grey'), end='')

    print(f" ({sum(stars_per_day)}{colored('*', 'yellow')})\n")
    print(f'({colored("*", "yellow")} 2 stars) '
          f'({colored("*", "cyan")} 1 star) '
          f'({colored("*", "grey")} 0 stars)\n')

    print(tabulate(table_rows, stralign='right', headers=[
        '\nDay',
        *['\n'.join([colored(y, 'cyan') for y in x.split('\n')])
            for x in ['----\nTime', '(Part 1)\nRank', '----\nScore']],
        *['\n'.join([colored(y, 'yellow') for y in x.split('\n')])
            for x in ['----\nTime', '(Part 2)\nRank', '----\nScore']]
    ]), '\n')

    if conf['private_leaderboards']:
        num_private_leaderboards = len(conf['private_leaderboards'])
        print(colored(f'You are a member of {num_private_leaderboards} '
                      f'private leaderboard(s).', 'grey'))
        print(colored(f'Use "advent stats {year} --private" to see them.\n', 'grey'))


def show_private_leaderboard(year, board_id):
    conf = config.get_config()
    r = requests.get(
                f'https://adventofcode.com/{year}/leaderboard/private/view/{board_id}',
                cookies={'session': conf['session_cookie']}
            )
    if '[Log In]' in r.text:
        print(colored('Session cookie is invalid or expired.', 'red'))
        return

    soup = BeautifulSoup(r.text, 'html.parser')

    intro_text = soup.select('article p')[0].text
    board_owner = soup.find('div', class_='user').contents[0].strip() \
        if 'This is your' in intro_text \
        else re.findall(r'private leaderboard of (.*) for', intro_text)[0]

    rows = soup.find_all('div', class_='privboard-row')[1:]

    top_score_len = len(rows[0].find_all(text=True, recursive=False)[0].strip())
    print(f"\n{board_owner}'s private leaderboard {colored(f'({board_id})', 'grey')}")
    print(f'\n{" "*(top_score_len+14)}1111111111222222'
            f'\n{" "*(top_score_len+5)}1234567890123456789012345')

    for row in rows:
        position = row.find('span', class_='privboard-position')
        if position is None or len(position) != 2:
            position = ' '
        else:
            position = position.text
        stars = row.find_all('span', class_=re.compile('privboard-star-*'))
        name = row.find('span', class_='privboard-name').text
        name_link = row.select('.privboard-name a')[0].attrs['href'] \
            if len(row.select('.privboard-name a')) else None
        score = row.find_all(text=True, recursive=False)[0].strip()

        print(f'{position} {score:>{top_score_len}}', end=' ')
        for span in stars:
            class_ = span.attrs['class'][0]
            if 'both' in class_:
                print(colored('*', 'yellow'), end='')
            elif 'firstonly' in class_:
                print(colored('*', 'cyan'), end='')
            elif 'unlocked' in class_:
                print(colored('*', 'grey'), end='')
            elif 'locked' in class_:
                print(' ', end='')

        print(f' {name}', end=' ')
        print(f'({colored(name_link, "blue")})' if name_link is not None else '')

    print()
    print(f'({colored("*", "yellow")} 2 stars) '
            f'({colored("*", "cyan")} 1 star) '
            f'({colored("*", "grey")} 0 stars)\n')

def private_leaderboard_stats(year):
    today = dt.today()
    if today.year <= int(year) and today.month < 12:
        print(colored(f'Defaulting to previous year ({today.year - 1}).', 'red'))
        year = str(today.year - 1)

    conf = config.get_config()
    if conf['private_leaderboards']:
        for board_id in conf['private_leaderboards']:
            show_private_leaderboard(year, board_id)
    else:
        r = requests.get(
                f'https://adventofcode.com/{year}/leaderboard/private',
                cookies={'session': conf['session_cookie']}
            )
        if '[Log In]' in r.text:
            print(colored('Session cookie is invalid or expired.', 'red'))
            return
        soup = BeautifulSoup(r.text, 'html.parser')

        links = soup.find_all('a', href=re.compile(r'/leaderboard/private/view'))

        if not links:
            print(colored('You are not a member of any private leaderboards', 'red'))
        else:
            for link in links:
                show_private_leaderboard(year, link.attrs['href'].split('/')[-1])

def test(year, day, solution_file='solution', input_file=None):

    if not os.path.exists(f'{year}/{day}/'):
        print(colored('Directory does not exist:', 'red'))
        print(colored(f'  "{os.getcwd()}/{year}/{day}/"', 'red'))
        return

    if input_file is not None:
        # check if input_file is a valid path file or a valid file in the current directory
        if os.path.exists(f'{os.getcwd()}/{year}/{day}/{input_file}'):
            input_file = f'{os.getcwd()}/{year}/{day}/{input_file}'
        elif os.path.exists(input_file):
            input_file = input_file
        else:
            print(colored('Example input file does not exist:', 'red'))
            print(colored(f'  {os.getcwd()}/{year}/{day}/{input_file}', 'red'))
    else:
        input_file = f'{os.getcwd()}/{year}/{day}/{INPUT_FILE_NAME}'

    print(f'Using input file: {input_file}')
    if solution_file != 'solution':
        if not os.path.exists(f'{year}/{day}/{solution_file}.py'):
            print(colored('Solution file does not exist:', 'red'))
            print(colored(f'  "{os.getcwd()}/{year}/{day}/{solution_file}.py"', 'red'))
            return
        print(colored(f'(Using {solution_file}.py)', 'red'))

    part1_answer, part2_answer = compute_answers(year, day,
                                                 file_path=input_file,
                                                 solution_file=solution_file)
    if part1_answer is not None:
        print(f'{colored("Part 1:", "cyan")} {part1_answer}')
        if part2_answer is not None:
            print(f'{colored("Part 2:", "yellow")} {part2_answer}')
    else:
        print(colored('No solution implemented', 'red'))
        return

    if solution_file != 'solution':
        part1_answer_orig, part2_answer_orig = compute_answers(year, day, file_path=input_file)
        if part1_answer == part1_answer_orig and part2_answer == part2_answer_orig:
            print(colored('Output matches solution.py', 'green'))
        else:
            print(colored('Output does not match solution.py', 'red'))


def submit(year, day, solution_file='solution'):

    if not os.path.exists(f'{year}/{day}/'):
        print(colored('Directory does not exist:', 'red'))
        print(colored(f'  "{os.getcwd()}/{year}/{day}/"', 'red'))
        return

    if solution_file != 'solution':
        if not os.path.exists(f'{year}/{day}/{solution_file}.py'):
            print(colored('Solution file does not exist:', 'red'))
            print(colored(f'  "{os.getcwd()}/{year}/{day}/{solution_file}.py"', 'red'))
            return
        print(colored(f'(Using {solution_file}.py)', 'red'))

    part1_answer, part2_answer = compute_answers(year, day, file_path=os.path.join(os.getcwd(), year, day, INPUT_FILE_NAME), solution_file=solution_file)

    status, response = None, None
    if part2_answer is not None:
        print('Submitting part 2...')
        status, response = submit_answer(year, day, 2, part2_answer)
    elif part1_answer is not None:
        print('Submitting part 1...')
        status, response = submit_answer(year, day, 1, part1_answer)
    else:
        print(colored('No solution implemented', 'red'))
        return

    if status == Status.PASS:
        print(colored('Correct!', 'green'), end=' ')
        if part2_answer is not None:
            print(colored('**', 'yellow'))
            print(f'Day {int(day)} complete!')
        elif part1_answer is not None:
            print(colored('*', 'cyan'))
            conf = config.get_config()
            r = requests.get(f'https://adventofcode.com/{year}/day/{int(day)}',
                             cookies={'session': conf['session_cookie']})
            soup = BeautifulSoup(r.text, 'html.parser')
            part2_html = soup.find_all('article', class_='day-desc')[1].decode_contents()

            # remove hyphens from title sections, makes markdown look nicer
            part2_html = re.sub('--- (.*) ---', r'\1', part2_html)

            # also makes markdown look better
            part2_html = part2_html.replace('\n\n', '\n')

            with open(f'{year}/{day}/prompt.md', 'a') as f:
                f.write(custom_markdownify(part2_html))
            print(f'Appended part 2 prompt to {year}/{day}/prompt.md')

    elif status == Status.FAIL:
        print(colored('Incorrect!', 'red'))

    elif status == Status.RATE_LIMIT:
        print(colored('Rate limited! Please wait before submitting again.', 'yellow'))

    elif status == Status.COMPLETED:
        print(colored("You've already completed this question.", 'yellow'))

    elif status == Status.NOT_LOGGED_IN:
        print(colored('Session cookie is invalid or expired.', 'red'))

    elif status == Status.UNKNOWN:
        print(colored('Something went wrong. Please view the output below:', 'red'))
        print(response)


def countdown(year, day):

    now = dt.now().astimezone(pytz.timezone('EST'))

    if now.year != int(year):
        print(colored(f'Date must be from the current year ({now.year}).', 'red'))
        return

    if now > dt(int(year), 12, int(day)).astimezone(pytz.timezone('EST')):
        print(colored('That puzzle has already been unlocked.', 'red'))
        return

    def curses_countdown(stdscr):  # pragma: no cover
        curses.cbreak()
        curses.halfdelay(2)
        curses.use_default_colors()
        if config.get_config()['disable_color']:
            for i in range(1, 4):
                curses.init_pair(i, -1, -1)
        else:
            curses.init_pair(1, curses.COLOR_MAGENTA, -1)
            curses.init_pair(2, curses.COLOR_YELLOW, -1)
            curses.init_pair(3, curses.COLOR_RED, -1)
        hours, minutes, seconds = get_time_until_unlock(year, day)
        while any((hours, minutes, seconds)):
            stdscr.erase()
            stdscr.addstr('advent-cli', curses.color_pair(1))
            stdscr.addstr(' countdown\n\n')
            stdscr.addstr(f'  {year} day {int(day)} will unlock in:\n', curses.color_pair(2))
            stdscr.addstr(f'  {hours} hours, {minutes} minutes, {seconds} seconds\n\n')
            stdscr.addstr('(press Q or CTRL+C to exit)', curses.color_pair(3))
            stdscr.refresh()
            stdscr.nodelay(1)
            key = stdscr.getch()
            if key == 27 or key == 113:
                raise KeyboardInterrupt
            hours, minutes, seconds = get_time_until_unlock(year, day)

    try:  # pragma: no cover
        curses.wrapper(curses_countdown)
        print(colored('Countdown finished', 'green'))
        time.sleep(1)  # wait an extra second, just in case the timing is slightly early
    except KeyboardInterrupt:  # pragma: no cover
        print(colored('Countdown cancelled', 'red'))
        sys.exit(1)
