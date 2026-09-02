#!/usr/bin/env python3

import argparse
from datetime import date, datetime, time, timedelta


def to_hm(td: timedelta) -> str:
    """
    Formats a timedelta object to display its total hours and minutes (HH:MM).
    Handles negative timedeltas.
    """
    total_seconds = int(td.total_seconds())  # Get total seconds as an integer

    # Determine the sign and work with absolute value
    is_negative = total_seconds < 0
    abs_total_seconds = abs(total_seconds)

    # Calculate hours and remaining seconds
    hours, remainder_seconds = divmod(abs_total_seconds, 3600)

    # Calculate minutes from remaining seconds
    minutes, _ = divmod(remainder_seconds, 60)

    # Format the output with leading zeros and the correct sign
    sign = "-" if is_negative else ""
    return f"{sign}{hours:02}:{minutes:02}"


def parse_clock(value: str) -> time:
    if len(value) != 5 or value[2] != ":" or not (value[:2] + value[3:]).isdigit():
        raise ValueError

    return datetime.strptime(value, "%H:%M").time()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate time off from a starting time, including optional time "
            "out of the office."
        )
    )
    parser.add_argument("start_time", help="Start time should be in HH:MM format")
    parser.add_argument(
        "out_of_office",
        nargs="?",
        help="Optional time away in HH:MM-HH:MM format",
    )
    args = parser.parse_args()

    try:
        args.start_time = parse_clock(args.start_time)
    except ValueError:
        parser.error("Start time must be a valid time in HH:MM format")

    args.away_duration = timedelta()
    if args.out_of_office:
        try:
            away_start_text, away_end_text = args.out_of_office.split("-")
            away_start = datetime.combine(date.today(), parse_clock(away_start_text))
            away_end = datetime.combine(date.today(), parse_clock(away_end_text))
            if away_end <= away_start:
                raise ValueError
            args.away_duration = away_end - away_start
        except ValueError:
            parser.error(
                "Time out of office must be a valid increasing range in "
                "HH:MM-HH:MM format"
            )

    return args


def calc(hour: int, minutes: int, away_duration: timedelta) -> None:
    time_in = datetime.combine(date.today(), time(hour, minutes))
    time_out = time_in + timedelta(hours=8, minutes=47) + away_duration
    time_now = datetime.now()

    print(f"Punch In: {time_in.time()}")
    if away_duration:
        print(f"Time Away from Office: {to_hm(away_duration)}")
    print(f"Punch Out by: {time_out.time()}")
    print("")
    print(f"Time Now: {time_now.time()}")

    remain = time_out - time_now
    print(f"Time Left: {to_hm(remain)}")


def main() -> None:
    args = parse_args()
    calc(args.start_time.hour, args.start_time.minute, args.away_duration)


if __name__ == "__main__":
    main()
