from struct_excel.transform import to_enrollment


def test_to_enrollment():
    from tests.test_data import (
        RAW,
        EXPECTED_COURSES,
        EXPECTED_ENROLLMENTS,
        EXPECTED_SESSIONS,
        EXPECTED_STUDENTS,
    )

    enrollments = to_enrollment(
        RAW, EXPECTED_STUDENTS, EXPECTED_COURSES, EXPECTED_SESSIONS
    )

    assert len(enrollments) == len(EXPECTED_ENROLLMENTS)

    for i, enroll in enumerate(enrollments):
        assert enroll.enrollment_id == EXPECTED_ENROLLMENTS[i].enrollment_id
        assert enroll.student_id == EXPECTED_ENROLLMENTS[i].student_id
        assert enroll.session_id == EXPECTED_ENROLLMENTS[i].session_id
        assert enroll.reg_date == EXPECTED_ENROLLMENTS[i].reg_date
        assert enroll.completed == EXPECTED_ENROLLMENTS[i].completed
        assert enroll.payment_status == EXPECTED_ENROLLMENTS[i].payment_status
        assert enroll.exception == EXPECTED_ENROLLMENTS[i].exception


def test_to_enrollment_empty():
    enrollments = to_enrollment([], [], [], [])
    assert enrollments == []


def test_to_enrollment_deduplication():
    from datetime import datetime
    from struct_excel.models import (
        Course,
        Gender,
        RawRow,
        Sector,
        CourseSession,
        CourseSessionMode,
        Student,
    )

    raw_dup = [
        RawRow(
            reg_date=datetime(2026, 1, 15),
            student_full_name="Student 1",
            student_email="student1@example.com",
            student_company="Company",
            student_job_title="Title",
            country="USA",
            exception="None",
            phone="123-456-7890",
            course="Feb 10 2026 | [Online] Python Basics [2hr]",
            gender="Male",
            sector="Private",
            supervisor_name="Supervisor",
            supervisor_email="supervisor@example.com",
            it_background="Yes",
            experience="2-5 years",
            completed="Yes",
            payment_status="Paid",
        ),
        RawRow(
            reg_date=datetime(2026, 1, 16),
            student_full_name="Student 1",
            student_email="student1@example.com",
            student_company="Company",
            student_job_title="Title",
            country="USA",
            exception="None",
            phone="098-765-4321",
            course="Feb 10 2026 | [Online] Python Basics [2hr]",
            gender="Male",
            sector="Private",
            supervisor_name="Supervisor",
            supervisor_email="supervisor@example.com",
            it_background="Yes",
            experience="2-5 years",
            completed="Yes",
            payment_status="Paid",
        ),
    ]
    students = [
        Student(
            student_id=1,
            full_name="Student 1",
            email="student1@example.com",
            gender=Gender.MALE,
            it_background=True,
            experience_min_years=2,
            experience_max_years=5,
            sector=Sector.PRIVATE,
            supervisor_id=1,
            company="company",
            job_title=None,
            country="MY",
            phone="1234567890",
        ),
    ]
    courses = [
        Course(course_id=1, course_name="Python Basics"),
    ]
    sessions = [
        CourseSession(
            session_id=1,
            course_id=1,
            start_datetime=datetime(2026, 2, 10),
            end_datetime=datetime(2026, 2, 10),
            mode=CourseSessionMode.ONLINE,
            duration=2.0,
        ),
    ]
    enrollments = to_enrollment(raw_dup, students, courses, sessions)
    assert len(enrollments) == 1
    assert enrollments[0].enrollment_id == 1


def test_to_enrollment_no_student_match():
    from datetime import datetime
    from struct_excel.models import (
        Course,
        Gender,
        RawRow,
        Sector,
        CourseSession,
        CourseSessionMode,
        Student,
    )

    raw = [
        RawRow(
            reg_date=datetime(2026, 1, 15),
            student_full_name="Unknown Student",
            student_email="unknown@example.com",
            student_company="Company",
            student_job_title="Title",
            country="USA",
            exception="None",
            phone="123-456-7890",
            course="Feb 10 2026 | [Online] Python Basics [2hr]",
            gender="Male",
            sector="Private",
            supervisor_name="Supervisor",
            supervisor_email="supervisor@example.com",
            it_background="Yes",
            experience="2-5 years",
            completed="Yes",
            payment_status="Paid",
        ),
    ]
    students = [
        Student(
            student_id=1,
            full_name="Student 1",
            email="student1@example.com",
            gender=Gender.MALE,
            it_background=True,
            experience_min_years=2,
            experience_max_years=5,
            sector=Sector.PRIVATE,
            supervisor_id=1,
            company="company",
            job_title=None,
            country="MY",
            phone="1234567890",
        ),
    ]
    courses = [
        Course(course_id=1, course_name="Python Basics"),
    ]
    sessions = [
        CourseSession(
            session_id=1,
            course_id=1,
            start_datetime=datetime(2026, 2, 10),
            end_datetime=datetime(2026, 2, 10),
            mode=CourseSessionMode.ONLINE,
            duration=2.0,
        ),
    ]
    enrollments = to_enrollment(raw, students, courses, sessions)
    assert len(enrollments) == 0
