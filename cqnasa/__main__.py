import argparse

from .apod import send_apod
from .sdo import send_sdo


def main():
    parser = argparse.ArgumentParser(
        prog="cqnasa",
        description="Send NASA images to QQ groups.",
    )
    parser.add_argument("job", choices=["apod", "sdo"], help="What to send.")
    args = parser.parse_args()
    if args.job == "apod":
        send_apod()
    else:
        send_sdo()


if __name__ == "__main__":
    main()
