from datetime import datetime
import calendar
import re
from struct_excel.models import (
    CourseParseResult,
    CourseSessionMode,
    Gender,
    Sector,
    PaymentStatus,
)


def parse_gender(value: str | Gender) -> Gender:
    if isinstance(value, Gender):
        return value
    value = str(value).strip().lower() if value is not None else ""
    if value == "male":
        return Gender.MALE
    if value == "female":
        return Gender.FEMALE
    return Gender.OTHER


def parse_sector(value: str | Sector | None) -> Sector:
    if isinstance(value, Sector):
        return value

    # TODO: Discuss the default value.
    if value is None:
        return Sector.STUDENT

    normalized = str(value).strip().lower()
    for sector in Sector:
        if normalized in {sector.name.lower(), sector.value.lower()}:
            return sector
    return Sector.STUDENT


def parse_experience(expr: str | None) -> tuple[int, int]:
    if expr is None:
        return 0, 0

    numbers = [int(num) for num in re.findall(r"\d+", str(expr))]
    if not numbers:
        return 0, 0
    if len(numbers) == 1:
        if "<" in expr:
            return 0, numbers[0]
        if ">" in expr:
            return numbers[0], 100
        return numbers[0], numbers[0]
    return min(numbers[0], numbers[1]), max(numbers[0], numbers[1])


def parse_bool_schema(value: str | None) -> bool:
    if value is None:
        return False
    return value.lower().strip() in ("yes", "true", "1")


def parse_payment_status(value: str | None) -> PaymentStatus:
    if value is None:
        return PaymentStatus.PENDING
    return (
        PaymentStatus.PAID if value.upper().strip() == "PAID" else PaymentStatus.PENDING
    )


def parse_course_session(raw_course: str) -> CourseParseResult:
    if "|" not in raw_course:
        raise ValueError(f"parse {raw_course} failed: '|' not found")

    left = raw_course.split("|")[0].strip()
    right = raw_course.split("|")[1]

    course_name, duration = _parse_course_name_duration(right)
    mode = _parse_mode(raw_course)
    datetime_range = _parse_datetime(left)

    return CourseParseResult(
        datetime_range=datetime_range,
        mode=mode,
        course_name=course_name,
        duration=duration,
    )


def _parse_course_name_duration(right_part: str) -> tuple[str, float]:
    course_name = ""
    duration = 0

    if "[Online]" in right_part:
        right_part = right_part.replace("[Online]", "").strip()

    match = re.search(r"(.*?)\s*\[(\d+(?:\.\d+)?hr?)\]", right_part)
    if match:
        course_name = match.group(1).strip()
        duration = float(match.group(2).strip("hr"))
    else:
        course_name = right_part.strip()
        duration = 0

    return course_name, duration


def _parse_mode(raw: str) -> CourseSessionMode:
    if "[online]" in raw.lower():
        return CourseSessionMode.ONLINE
    return CourseSessionMode.OFFLINE


def _parse_datetime(left_part: str) -> list[tuple[datetime, datetime]]:
    if "&" in left_part and re.search(r"\d{4}", left_part):
        return _parse_multi_range(left_part)

    # Match `Feb 21 2026 (to Feb 26 2026)` style.
    m = re.match(r"(.+)\(to\s+(.+)\)", left_part)
    if m:
        start = datetime.strptime(m.group(1).strip(), "%b %d %Y")
        end = datetime.strptime(m.group(2).strip(), "%b %d %Y")
        return [(start, end)]

    # Match `Feb 21 2026 @ 9.30am` style.
    m = re.match(r"(.+?)\s*@\s*([\d\.]+)(am|pm)", left_part, re.I)
    if m:
        date_str = m.group(1).strip()
        time_str = m.group(2)
        meridiem = m.group(3).lower()

        dt = datetime.strptime(date_str, "%b %d %Y")
        if "." in time_str:
            hour, minute = map(int, time_str.split("."))
        else:
            hour, minute = int(time_str), 0

        if meridiem == "pm" and hour != 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0

        start = dt.replace(hour=hour, minute=minute)
        end = start
        return [(start, end)]

    # Match `Feb 21 2026` style.
    dt = datetime.strptime(left_part, "%b %d %Y")
    return [(dt, dt)]


def _parse_multi_range(left_part: str) -> list[tuple[datetime, datetime]]:
    left_part = left_part.strip()

    m = re.search(r"\d{4}", left_part)
    if not m:
        raise ValueError(f"year not found in {left_part}")

    year = int(m.group())
    left_part = re.sub(r"\d{4}", "", left_part).strip()
    parts = [p.strip() for p in left_part.split("&")]

    result = []

    for part in parts:
        m = re.match(r"([A-Za-z]+)\s+(\d+)-(\d+)", part)
        if not m:
            continue

        month_str = m.group(1)
        d1 = int(m.group(2))
        d2 = int(m.group(3))
        month = list(calendar.month_abbr).index(month_str[:3])

        start = datetime(year, month, d1)
        end = datetime(year, month, d2)

        result.append((start, end))

    return result
