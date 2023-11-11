import argparse
import json

import tum_moodle_downloader.globals as globals
import tum_moodle_downloader.authentication as authentication
import tum_moodle_downloader.credential_handler as credential_handler
import tum_moodle_downloader.moodle_downloader as moodle_downloader

def setup_parser():
    arg_parser = argparse.ArgumentParser()
    subparsers = arg_parser.add_subparsers()

    # 'List' subcommand
    list_command_description = "List available resources of the specified course or, if no course is specified, list available courses"
    list_parser = subparsers.add_parser(
        "list",
        description=list_command_description,
        help=list_command_description
    )

    # python src/main.py list -f "<course name>"
    list_parser.add_argument(
        '-f', '--files',
        action='store_true',
        help="only print available files"
    )
    list_parser.add_argument(
        "course",
        type=str,
        nargs='?',
        default='*',
        help="name of the course of which the resources are to be listed"
    )
    
    list_parser.set_defaults(func=moodle_downloader.list_resources)

    # 'Download' subcommand
    download_command_description = "Download resources which match a file_pattern from a course into a destination path. " \
                                   "If parameters are omitted they are retrieved from  course_config.json"
    download_parser = subparsers.add_parser(
        "download",
        description=download_command_description,
        help=download_command_description
    )

    download_parser.add_argument(
        "--course",
        type=str,
        help="name of the course from which to download"
    )
    download_parser.add_argument(
        "--file_pattern",
        type=str,
        help="name pattern for the resources which are to be downloaded"
    )
    download_parser.add_argument(
        "--destination",
        type=str,
        help="path at which the download(s) should be stored"
    )

    download_parser.set_defaults(func=moodle_downloader.download)

    return arg_parser


def main():
    arg_parser = setup_parser()
    args = arg_parser.parse_args()

    with open(globals.DOWNLOAD_CONFIG_PATH, mode='r', encoding='utf-8') as main_config:
        config_data = json.load(main_config)

    username, password = credential_handler.get_credentials()

    session = authentication.start_session(
        username,
        password
    )
    if session is None:
        print('Could not start Moodle session.')
        exit(1)

    globals.set_global_session(session)

    # Call the function which is set based on the command provided in the arguments
    # (see 'setup_parser' above for details)
    args.func(args)

if __name__ == "__main__":
    main()
