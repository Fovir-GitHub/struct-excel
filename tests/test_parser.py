import pytest
from datetime import datetime
from struct_excel.models import PaymentStatus, CourseSessionMode
from struct_excel.parser import (
    parse_bool_schema,
    parse_course_session,
    parse_payment_status,
)


class TestParseCourseSession:
    def test_parse_simple_date(self):
        result = parse_course_session("Feb 10 2026 | Python Basics [2hr]")

        assert result.course_name == "Python Basics"
        assert result.duration == 2.0
        assert result.mode == CourseSessionMode.OFFLINE
        assert result.datetime_range == [(datetime(2026, 2, 10), datetime(2026, 2, 10))]

    def test_parse_with_online(self):
        result = parse_course_session("Feb 10 2026 | [Online] Python Basics [2hr]")

        assert result.course_name == "Python Basics"
        assert result.duration == 2.0
        assert result.mode == CourseSessionMode.ONLINE

    def test_parse_with_offline(self):
        result = parse_course_session("Feb 10 2026 | [Offline] Python Basics [2hr]")

        assert result.course_name == "[Offline] Python Basics"
        assert result.duration == 2.0
        assert result.mode == CourseSessionMode.OFFLINE

    def test_parse_date_range(self):
        result = parse_course_session(
            "Feb 21 2026 (to Feb 26 2026) | Python Basics [30hr]"
        )

        assert result.course_name == "Python Basics"
        assert result.duration == 30.0
        assert result.datetime_range == [(datetime(2026, 2, 21), datetime(2026, 2, 26))]

    def test_parse_with_time(self):
        result = parse_course_session("Feb 21 2026 @ 9.30am | Python Basics [2hr]")

        assert result.course_name == "Python Basics"
        assert result.duration == 2.0
        assert result.datetime_range == [
            (datetime(2026, 2, 21, 9, 30), datetime(2026, 2, 21, 9, 30))
        ]

    def test_parse_with_time_pm(self):
        result = parse_course_session("Feb 21 2026 @ 2.00pm | Python Basics [2hr]")

        assert result.datetime_range[0][0].hour == 14

    def test_parse_no_duration(self):
        result = parse_course_session("Feb 10 2026 | Python Basics")

        assert result.course_name == "Python Basics"
        assert result.duration == 0.0

    def test_parse_no_pipe_raises(self):
        with pytest.raises(ValueError):
            parse_course_session("Invalid Course")

    def test_parse_malaysia_time(self):
        result = parse_course_session(
            "Feb 19 2026 (to Feb 20 2026) @ 9.30am MYT | [Online] Cybersecurity Tools [3h]"
        )

        assert result.course_name == "Cybersecurity Tools"
        assert result.duration == 3.0
        assert result.mode == CourseSessionMode.ONLINE

    def test_parse_hour_format_no_hr(self):
        result = parse_course_session("Feb 10 2026 | Python Basics [2]")

        assert result.duration == 0.0

    def test_parse_hour_format_with_hr(self):
        result = parse_course_session("Feb 10 2026 | Python Basics [2hr]")

        assert result.duration == 2.0

    def test_parse_hour_format_hours(self):
        result = parse_course_session("Feb 10 2026 | Python Basics [2 hours]")

        assert result.duration == 0.0

    def test_multiple_time_range(self):
        result = parse_course_session("Jan 12-14 & Jan 20-21 2026 | PECB CISO")

        assert set(map(tuple, result.datetime_range)) == {
            (datetime(2026, 1, 12), datetime(2026, 1, 14)),
            (datetime(2026, 1, 20), datetime(2026, 1, 21)),
        }
        assert result.course_name == "PECB CISO"
        assert result.duration == 0.0
        assert result.mode == CourseSessionMode.OFFLINE


class TestParseBoolSchema:
    def test_none_returns_false(self):
        assert parse_bool_schema(None) is False

    def test_yes_returns_true(self):
        assert parse_bool_schema("yes") is True

    def test_yes_uppercase_returns_true(self):
        assert parse_bool_schema("YES") is True

    def test_true_returns_true(self):
        assert parse_bool_schema("true") is True

    def test_true_uppercase_returns_true(self):
        assert parse_bool_schema("TRUE") is True

    def test_one_returns_true(self):
        assert parse_bool_schema("1") is True

    def test_one_with_spaces_returns_true(self):
        assert parse_bool_schema("  1  ") is True

    def test_other_returns_false(self):
        assert parse_bool_schema("no") is False

    def test_other_returns_false_2(self):
        assert parse_bool_schema("false") is False

    def test_other_returns_false_3(self):
        assert parse_bool_schema("0") is False


class TestParsePaymentStatus:
    def test_none_returns_pending(self):
        assert parse_payment_status(None) == PaymentStatus.PENDING

    def test_paid_uppercase_returns_paid(self):
        assert parse_payment_status("PAID") == PaymentStatus.PAID

    def test_paid_lowercase_returns_paid(self):
        assert parse_payment_status("paid") == PaymentStatus.PAID

    def test_paid_with_spaces_returns_paid(self):
        assert parse_payment_status("  PAID  ") == PaymentStatus.PAID

    def test_pending_returns_pending(self):
        assert parse_payment_status("PENDING") == PaymentStatus.PENDING

    def test_other_returns_pending(self):
        assert parse_payment_status("ABC") == PaymentStatus.PENDING
