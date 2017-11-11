import argparse
import json
import os
import sys
import subprocess

from datetime import datetime
from USYDecho360.EchoCourse import EchoCourse
from USYDecho360.EchoDownloader import EchoDownloader
import USYDecho360.phantomjs_binary_downloader as pbd


_DEFAULT_BEFORE_DATE = datetime(2900, 1, 1).date()
_DEFAULT_AFTER_DATE = datetime(1100, 1, 1).date()

def try_parse_date(date_string, fmt):
    try:
        return datetime.strptime(date_string, fmt).date()
    except:
        print("Error parsing date input:", sys.exc_info())
        sys.exit(1)

def handle_args():
    parser = argparse.ArgumentParser(description="Download lectures from USYD's Echo360 portal.")
    parser.add_argument("--uuid", "-u",
                        required=True,
                        help="Echo360 UUID for the course, which is found in \
                              the URL of the course's video lecture page (e.g. \
                              '115f3def-7371-4e98-b72f-6efe53771b2a' in \
                              http://recordings.engineering.illinois.edu/ess/portal/section/115f3def-7371-4e98-b72f-6efe53771b2a)",
                        metavar="COURSE_UUID")
    parser.add_argument("--output", "-o",
                        help="Path to the desired output directory The output \
                             directory must exist. Otherwise the current \
                             directory is used.",
                        metavar="OUTPUT_PATH")
    parser.add_argument("--after-date", "-a",
                        dest="after_date",
                        help="Only download lectures newer than AFTER_DATE \
                             (inclusive). Note: this may be combined with \
                             --before-date.",
                        metavar="AFTER_DATE(YYYY-MM-DD)")
    parser.add_argument("--before-date", "-b",
                        dest="before_date",
                        help="Only download lectures older than BEFORE_DATE \
                              (inclusive). Note: this may be combined with \
                              --after-date",
                        metavar="BEFORE_DATE(YYYY-MM-DD)")
    parser.add_argument("--unikey", "-k",
                        dest="unikey",
                        help="Your unikey for your University of \
                              Sydney elearning account",
                        metavar="UNIKEY")
    parser.add_argument("--password", "-p",
                        dest="password",
                        help="Your password for your University of \
                              Sydney elearning account",
                        metavar="PASSWORD")
    parser.add_argument("--download-phantomjs-binary",
                        action='store_true',
                        default=False,
                        dest="download_binary",
                        help="Force the usydEcho360.py script to download a local \
                              binary file for phantomjs (will override system bin)")

    args = vars(parser.parse_args())
    course_uuid = args["uuid"]

    output_path = os.path.expanduser(args["output"]) if args["output"] is not None else "default_out_path"
    output_path = output_path if os.path.isdir(output_path) else "default_out_path"

    after_date = try_parse_date(args["after_date"], "%Y-%m-%d") if args["after_date"] else _DEFAULT_AFTER_DATE
    before_date = try_parse_date(args["before_date"], "%Y-%m-%d") if args["before_date"] else _DEFAULT_BEFORE_DATE

    username = args["unikey"]
    password = args["password"]

    return (course_uuid, output_path, after_date, before_date, username, password, args['download_binary'])

def main(use_local_binary):
    course_uuid, output_path, after_date, before_date, username, password, download_binary = handle_args()

    if download_binary:
        download_phantomjs_binary(manual=True)
        exit(0)

    course = EchoCourse(course_uuid)
    downloader = EchoDownloader(course, output_path, date_range=(after_date, before_date), username=username, password=password, use_local_binary=use_local_binary)
    downloader.download_all()

def _blow_up(self, str, e):
    print(str)
    print("Exception: {}".format(str(e)))
    sys.exit(1)

def download_phantomjs_binary(manual=False):
    print('='*65)
    if not manual:
        print('Binary file of PhantomJS not found, will initiate a download process now...')
    pbd.download()
    print('Done!')
    print('='*65)

if __name__ == '__main__':
    # NOTE: local binary will always override system PATH binary
    use_local_binary = True

    # First test for existance of local phantomjs binary file
    if not os.path.isfile(pbd.get_phantomjs_bin()):
        # If failed, then test for existance of phantomjs in PATH
        with open(os.devnull, 'w')  as FNULL:
            try:
                subprocess.check_output(['phantomjs','.'], stderr=FNULL)
            except OSError:
                # None exists, download binary file
                # Initiate downloading binary file
                download_phantomjs_binary()
            except subprocess.CalledProcessError:
                # expected behaviour if binary exists
                use_local_binary = False
    main(use_local_binary)
