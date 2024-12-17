import argparse
from datetime import datetime as dt

from . import commands
from ._version import __version__
from .utils import CustomHelpFormatter

from termcolor import colored

def main():
    parser = argparse.ArgumentParser(formatter_class=CustomHelpFormatter)
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'advent-cli {__version__}'
    )
    command_subparsers = parser.add_subparsers(
        dest='command', description='use advent {subcommand} --help for arguments', required=True
    )
    parser_get = command_subparsers.add_parser(
        'get',
        help='download prompt and input, generate solution template',
        formatter_class=CustomHelpFormatter
    )

    parser_subparsers = parser_get.add_subparsers(dest="subcommand", help="use advent get puzzle date to get input", required=True)
    puzzle_parser = parser_subparsers.add_parser('puzzle', help="use advent get puzzle date to get input")
    solution_parser = parser_subparsers.add_parser('solution', help="use advent get solution date to get input")
    
    puzzle_parser.add_argument(
        'date',
        help='the year and day in YYYY/DD format (e.g. "2021/01") or year to get all puzzles from that year'
    )

    solution_parser.add_argument(
        'date',
        help='the year and day in YYYY/DD format (e.g. "2021/01") or "year" to get all solutions from that year'
    )

    parser_stats = command_subparsers.add_parser(
        'stats',
        help='show personal stats or private leaderboards',
        formatter_class=CustomHelpFormatter
    )
    parser_stats.add_argument(
        'year',
        nargs='?',
        default=dt.now().year,
        help='year to show stats for, defaults to current year'
    )
    parser_stats.add_argument(
        '-p', '--private',
        dest='show_private',
        action='store_true',
        help='show private leaderboard(s)'
    )
    parser_test = command_subparsers.add_parser(
        'test',
        help='run solution and output answers without submitting',
        formatter_class=CustomHelpFormatter
    )
    parser_test.add_argument(
        'date',
        help='the year and day in YYYY/DD format (e.g. "2021/01")'
    )
    parser_test.add_argument(
        '-e', '--example',
        dest='run_example',
        action='store_true',
        help='use example_input.txt for input'
    )
    parser_test.add_argument(
        '-f', '--solution-file',
        dest='solution_file',
        default='solution',
        help='solution file to run instead of solution.py\n'
             '(e.g. "solution2" for solution2.py)'
    )
    parser_submit = command_subparsers.add_parser(
        'submit',
        help='run solution and submit answers',
        formatter_class=CustomHelpFormatter
    )
    parser_submit.add_argument(
        'date',
        help='the year and day in YYYY/DD format (e.g. "2021/01")'
    )
    parser_submit.add_argument(
        '-f', '--solution-file',
        dest='solution_file',
        default='solution',
        help='solution file to run instead of solution.py\n'
             '(e.g. "solution2" for solution2.py)\n'
             '*only works if answers not yet submitted*'
    )
    parser_countdown = command_subparsers.add_parser(
        'countdown',
        help='display countdown to puzzle unlock',
        formatter_class=CustomHelpFormatter
    )
    parser_countdown.add_argument(
        'date',
        help='the year and day in YYYY/DD format (e.g. "2021/01")'
    )
    args = parser.parse_args()

    if args.command == 'get':
        date = args.date.split('/')
        if len(date) == 0:
            print(colored('Invalid date format. Please use YYYY/DD format.', 'red'))
        
        year = date[0]
        day = date[1] if len(date) > 1 else None

        if args.subcommand == 'puzzle':
            commands.get(year, day)
        elif args.subcommand == 'solution':
            commands.get_solution(year, day)

    elif args.command == 'stats':
        if args.show_private:
            commands.private_leaderboard_stats(args.year)
        else:
            commands.stats(args.year)

    elif args.command == 'test':
        year, day = args.date.split('/')
        commands.test(year, day, solution_file=args.solution_file, example=args.run_example)

    elif args.command == 'submit':
        year, day = args.date.split('/')
        commands.submit(year, day, solution_file=args.solution_file)

    elif args.command == 'countdown':
        year, day = args.date.split('/')
        commands.countdown(year, day)
