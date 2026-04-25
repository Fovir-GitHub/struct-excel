# TODO: Add transformation for `student`,
# `course`, `session`, `supervisor`,
# and `enrollment`.

import re
from collections.abc import Iterable, Mapping
from datetime import date, datetime, time
from typing import Any

from models import Course, Enrollment, RawRow, Session, SessionMode, Student, Supervisor


def to_supervisor(raw: list[RawRow]) -> list[Supervisor]:
    return []


def to_course(raw: list[RawRow]) -> list[Course]:
    return []


def to_student(raw: list[RawRow], supervisors: list[Supervisor]) -> list[Student]:
    return []


def to_session(raw: list[RawRow], courses: list[Course]) -> list[Session]:
    return []


"""----------------------------Enrollment Table----------------------------"""


_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _clean_text(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).replace("\u200b", "").strip()
    if text.lower() == "none":
        return ""
    return re.sub(r"\s+", " ", text)


def _normalize_email(value: Any) -> str:
    return _clean_text(value).lower()


def _normalize_lookup_text(value: Any) -> str:
    return _clean_text(value).lower()


def _normalize_mode(value: Any) -> str:
    if hasattr(value, "value"):
        value = value.value
    mode = _normalize_lookup_text(value)
    if "online" in mode:
        return SessionMode.ONLINE.value
    if "offline" in mode:
        return SessionMode.OFFLINE.value
    return mode


def _record_value(record: Any, *names: str) -> Any:
    if isinstance(record, Mapping):
        lowered = {str(key).strip().lower(): value for key, value in record.items()}
        for name in names:
            value = lowered.get(name.lower())
            if value is not None:
                return value
        return None

    for name in names:
        if hasattr(record, name):
            return getattr(record, name)
    return None


def _iter_records(source: Any) -> Iterable[Any]:
    if source is None:
        return []

    if hasattr(source, "iter_rows"):
        rows = source.iter_rows(values_only=True)
        try:
            headers = next(rows)
        except StopIteration:
            return []

        normalized_headers = [
            str(header).strip() if header is not None else "" for header in headers
        ]
        return (
            {
                header: value
                for header, value in zip(normalized_headers, row, strict=False)
                if header
            }
            for row in rows
            if any(value is not None for value in row)
        )

    return source


def _add_unique(mapping: dict[Any, Any | None], key: Any, value: Any) -> None:
    if key in mapping and mapping[key] != value:
        mapping[key] = None
        return
    mapping[key] = value


def _parse_course_start_datetime(course_str: Any) -> datetime | None:
    if not text:
        return None

    date_part = text.split("|", 1)[0]
    date_match = re.search(
        r"\b(?P<month>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
        r"[a-z]*\s+(?P<day>\d{1,2})",
        date_part,
        flags=re.IGNORECASE,
    )
    year_match = re.search(r"\b(?P<year>\d{4})\b", date_part)
    if not date_match or not year_match:
        return None

    month = _MONTHS[date_match.group("month")[:3].lower()]
    day = int(date_match.group("day"))
    year = int(year_match.group("year"))
    parsed_time = time()

    time_match = re.search(
        r"@\s*(?P<hour>\d{1,2})(?:[.:](?P<minute>\d{1,2}))?\s*(?P<ampm>am|pm)",
        date_part,
        flags=re.IGNORECASE,
    )
    if time_match:
        hour = int(time_match.group("hour"))
        minute = int(time_match.group("minute") or 0)
        ampm = time_match.group("ampm").lower()
        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        parsed_time = time(hour, minute)

    try:
        return datetime.combine(date(year, month, day), parsed_time)
    except ValueError:
        return None


def _coerce_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, time())

    text = _clean_text(value)
    if not text:
        return None

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

    return None


def _course_name_from_raw(course_str: Any) -> str:
    text = _clean_text(course_str)
    if "|" not in text:
        return text
    return _clean_text(text.split("|", 1)[1])


def _course_name_aliases(course_name: Any) -> list[str]:
    name = _clean_text(course_name)
    aliases: list[str] = []

    def add(alias: str) -> None:
        normalized = _normalize_lookup_text(alias)
        if normalized and normalized not in aliases:
            aliases.append(normalized)

    add(name)

    without_online = re.sub(r"^\[online\]\s*", "", name, flags=re.IGNORECASE)
    add(without_online)

    duration_suffix = (
        r"\s*\[(?:\d+(?:\.\d+)?\s*(?:h|hr|hrs|hour|hours))\]\s*$"
    )
    add(re.sub(duration_suffix, "", name, flags=re.IGNORECASE))
    add(re.sub(duration_suffix, "", without_online, flags=re.IGNORECASE))

    return aliases


def _course_mode_from_raw(course_str: Any) -> str:
    if re.search(r"\[online\]", _clean_text(course_str), flags=re.IGNORECASE):
        return SessionMode.ONLINE.value
    return SessionMode.OFFLINE.value


def _build_student_lookup(students: Any) -> dict[str, Any]:
    student_by_email: dict[str, Any] = {}
    for student in _iter_records(students):
        email = _normalize_email(_record_value(student, "email"))
        student_id = _record_value(student, "student_id")
        if email and student_id is not None:
            student_by_email[email] = student_id
    return student_by_email


def _build_course_lookup(
    courses: Any,
) -> tuple[dict[str, Any | None], dict[str, Any | None]]:
    exact_course_by_name: dict[str, Any | None] = {}
    alias_course_by_name: dict[str, Any | None] = {}
    for course in _iter_records(courses):
        course_id = _record_value(course, "course_id")
        course_name = _record_value(course, "course_name")
        if course_id is None or not _clean_text(course_name):
            continue

        aliases = _course_name_aliases(course_name)
        if not aliases:
            continue

        _add_unique(exact_course_by_name, aliases[0], course_id)
        for alias in aliases[1:]:
            _add_unique(alias_course_by_name, alias, course_id)

    return exact_course_by_name, alias_course_by_name


def _lookup_course_id(
    course_lookup: tuple[dict[str, Any | None], dict[str, Any | None]],
    raw_course_name: str,
) -> Any | None:
    exact_course_by_name, alias_course_by_name = course_lookup
    aliases = _course_name_aliases(raw_course_name)
    if not aliases:
        return None

    exact_match = exact_course_by_name.get(aliases[0])
    if exact_match is not None:
        return exact_match

    for alias in aliases[1:]:
        exact_match = exact_course_by_name.get(alias)
        if exact_match is not None:
            return exact_match

    for alias in aliases:
        alias_match = alias_course_by_name.get(alias)
        if alias_match is not None:
            return alias_match

    return None


def _build_session_lookups(
    sessions: Any,
) -> tuple[
    dict[tuple[Any, datetime, str], Any | None],
    dict[tuple[Any, datetime], Any | None],
    dict[tuple[Any, date, str], Any | None],
    dict[tuple[Any, date], Any | None],
    dict[tuple[datetime, str], Any | None],
    dict[datetime, Any | None],
    dict[tuple[date, str], Any | None],
    dict[date, Any | None],
]:
    by_course_datetime_mode: dict[tuple[Any, datetime, str], Any | None] = {}
    by_course_datetime: dict[tuple[Any, datetime], Any | None] = {}
    by_course_date_mode: dict[tuple[Any, date, str], Any | None] = {}
    by_course_date: dict[tuple[Any, date], Any | None] = {}
    by_datetime_mode: dict[tuple[datetime, str], Any | None] = {}
    by_datetime: dict[datetime, Any | None] = {}
    by_date_mode: dict[tuple[date, str], Any | None] = {}
    by_date: dict[date, Any | None] = {}

    for session in _iter_records(sessions):
        session_id = _record_value(session, "session_id")
        course_id = _record_value(session, "course_id")
        start_datetime = _coerce_datetime(_record_value(session, "start_datetime"))
        mode = _normalize_mode(_record_value(session, "mode"))
        if session_id is None or start_datetime is None:
            continue

        if course_id is not None:
            if mode:
                _add_unique(
                    by_course_datetime_mode,
                    (course_id, start_datetime, mode),
                    session_id,
                )
                _add_unique(
                    by_course_date_mode,
                    (course_id, start_datetime.date(), mode),
                    session_id,
                )
            _add_unique(by_course_datetime, (course_id, start_datetime), session_id)
            _add_unique(by_course_date, (course_id, start_datetime.date()), session_id)

        if mode:
            _add_unique(by_datetime_mode, (start_datetime, mode), session_id)
            _add_unique(by_date_mode, (start_datetime.date(), mode), session_id)
        _add_unique(by_datetime, start_datetime, session_id)
        _add_unique(by_date, start_datetime.date(), session_id)

    return (
        by_course_datetime_mode,
        by_course_datetime,
        by_course_date_mode,
        by_course_date,
        by_datetime_mode,
        by_datetime,
        by_date_mode,
        by_date,
    )


def _lookup_session_id(
    lookups: tuple[
        dict[tuple[Any, datetime, str], Any | None],
        dict[tuple[Any, datetime], Any | None],
        dict[tuple[Any, date, str], Any | None],
        dict[tuple[Any, date], Any | None],
        dict[tuple[datetime, str], Any | None],
        dict[datetime, Any | None],
        dict[tuple[date, str], Any | None],
        dict[date, Any | None],
    ],
    course_id: Any,
    start_datetime: datetime,
    mode: str,
) -> Any | None:
    (
        by_course_datetime_mode,
        by_course_datetime,
        by_course_date_mode,
        by_course_date,
        by_datetime_mode,
        by_datetime,
        by_date_mode,
        by_date,
    ) = lookups

    candidates = []
    if course_id is not None:
        if mode:
            candidates.append(
                by_course_datetime_mode.get((course_id, start_datetime, mode))
            )
        candidates.append(by_course_datetime.get((course_id, start_datetime)))
        if mode:
            candidates.append(
                by_course_date_mode.get((course_id, start_datetime.date(), mode))
            )
        candidates.append(by_course_date.get((course_id, start_datetime.date())))
        return next(
            (session_id for session_id in candidates if session_id is not None),
            None,
        )

    if mode:
        candidates.append(by_datetime_mode.get((start_datetime, mode)))
    candidates.append(by_datetime.get(start_datetime))
    if mode:
        candidates.append(by_date_mode.get((start_datetime.date(), mode)))
    candidates.append(by_date.get(start_datetime.date()))

    return next(
        (session_id for session_id in candidates if session_id is not None),
        None,
    )


def to_enrollment(
    raw: list[RawRow],
    students: list[Student] | Any,
    courses_or_sessions: list[Course] | list[Session] | Any,
    sessions: list[Session] | Any | None = None,
) -> list[Enrollment]:
    
    courses = courses_or_sessions if sessions is not None else None
    sessions_source = sessions if sessions is not None else courses_or_sessions

    student_by_email = _build_student_lookup(students)
    course_lookup = _build_course_lookup(courses)
    session_lookups = _build_session_lookups(sessions_source)
    require_course_match = courses is not None

    enrollments: list[Enrollment] = []
    for row in raw:
        student_id = student_by_email.get(_normalize_email(row.student_email))
        if student_id is None:
            continue

        raw_course_name = _course_name_from_raw(row.course)
        course_id = _lookup_course_id(course_lookup, raw_course_name)
        if require_course_match and course_id is None:
            continue

        start_datetime = _parse_course_start_datetime(row.course)
        if start_datetime is None:
            continue

        session_id = _lookup_session_id(
            session_lookups,
            course_id,
            start_datetime,
            _course_mode_from_raw(row.course),
        )
        if session_id is None:
            continue

        completed = _normalize_lookup_text(row.completed) in ("yes", "true", "1")

        enrollments.append(
            Enrollment(
                enrollment_id=len(enrollments) + 1,
                student_id=student_id,
                session_id=session_id,
                reg_date=_coerce_datetime(row.reg_date) or row.reg_date,
                completed=completed,
                payment_status=_clean_text(row.payment_status),
                exception=_clean_text(row.exception),
            )
        )

    return enrollments
