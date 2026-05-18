# TODO: Add transformation for `student`,
# `course`, `session`, `supervisor`,
# and `enrollment`.

import logging
from struct_excel.models import (
    Course,
    Enrollment,
    RawRow,
    CourseSession,
    Student,
    Supervisor,
)
from struct_excel.parser import (
    parse_bool_schema,
    parse_course_session,
    parse_payment_status,
    parse_course_session,
    parse_gender,
    parse_experience,
    parse_sector,
)

logger = logging.getLogger(__name__)


def to_supervisor(raw: list[RawRow]) -> list[Supervisor]:
    sups: list[Supervisor] = []
    seen = set()

    for entry in raw:
        email = entry.supervisor_email
        name = entry.supervisor_name
        if email is None or name is None or email == "" or name == "":
            continue
        if email in seen:
            continue
        seen.add(email)
        sups.append(
            Supervisor(supervisor_id=len(sups) + 1, full_name=name, email=email)
        )
    return sups


def to_course(raw: list[RawRow]) -> list[Course]:
    courses: list[Course] = []
    duplicate = set()

    for row in raw:
        parsed = parse_course_session(row.course)
        course_name = parsed.course_name
        if course_name in duplicate:
            continue
        duplicate.add(course_name)

        courses.append(
            Course(
                course_id=len(courses) + 1,
                course_name=course_name,
            )
        )

    return courses


def to_student(raw: list[RawRow], supervisors: list[Supervisor]) -> list[Student]:
    supervisor_lookup = {supervisor.email: supervisor for supervisor in supervisors}

    students: list[Student] = []
    seen = set()

    for row in raw:
        supervisor_id: int | None = None
        if row.supervisor_email is not None and row.supervisor_name is not None:
            sup = supervisor_lookup.get(row.supervisor_email)
            if not sup:
                logger.warning(
                    f"lookup supervisor id failed: email={row.supervisor_email}"
                )
                supervisor_id = None
            else:
                supervisor_id = sup.supervisor_id

        gender = parse_gender(row.gender)
        experience_min_years, experience_max_years = parse_experience(row.experience)
        it_background = parse_bool_schema(row.it_background)
        sector = parse_sector(row.sector)

        dedupe_key = row.student_email
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        student = Student(
            student_id=len(students) + 1,
            full_name=row.student_full_name,
            email=row.student_email,
            gender=gender,
            it_background=it_background,
            experience_min_years=experience_min_years,
            experience_max_years=experience_max_years,
            sector=sector,
            supervisor_id=supervisor_id,
            company=row.student_company,
            job_title=row.student_job_title,
            country=row.country,
            phone=row.phone,
        )

        students.append(student)

    return students


def to_session(raw: list[RawRow], courses: list[Course]) -> list[CourseSession]:
    sessions: list[CourseSession] = []
    session_id = 1
    seen = set()

    for entry in raw:
        try:
            course_session = parse_course_session(entry.course)
            existed_course = _select_course_by_name(courses, course_session.course_name)
        except ValueError as e:
            logger.warning(f"skip invalid session: {entry.course}, err: {e}")
            continue

        for start, end in course_session.datetime_range:
            dedup_key = (
                existed_course.course_id,
                start,
                end,
                course_session.duration,
            )
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            sessions.append(
                CourseSession(
                    session_id=session_id,
                    course_id=existed_course.course_id,
                    start_datetime=start,
                    end_datetime=end,
                    mode=course_session.mode,
                    duration=course_session.duration,
                )
            )
            session_id += 1

    return sessions


def to_enrollment(
    raw: list[RawRow],
    students: list[Student],
    courses: list[Course],
    sessions: list[CourseSession],
) -> list[Enrollment]:
    student_id_by_email = {student.email: student.student_id for student in students}
    course_id_by_name = {course.course_name: course.course_id for course in courses}
    session_id_by_course_session = {
        (
            session.course_id,
            session.start_datetime,
            session.end_datetime,
            session.mode,
        ): session.session_id
        for session in sessions
    }

    seen = set()
    enrollments: list[Enrollment] = []
    for row in raw:
        student_id = student_id_by_email.get(row.student_email)
        if student_id is None:
            logger.warning(f"can not find student id (email={row.student_email})")
            continue

        try:
            course_session = parse_course_session(row.course)
        except ValueError as e:
            logger.warning(f"skip invalid enrollment: {row.course} err: {e}")
            continue

        course_id = course_id_by_name.get(course_session.course_name)
        if course_id is None:
            logger.warning(
                f"can not find course id (course_name={course_session.course_name})"
            )
            continue

        for start, end in course_session.datetime_range:
            session_id = session_id_by_course_session.get(
                (
                    course_id,
                    start,
                    end,
                    course_session.mode,
                )
            )
            if session_id is None:
                logger.warning(
                    f"can not find session id (course_name={course_session.course_name})"
                )
                continue

            dedup_key = (student_id, session_id)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            completed = parse_bool_schema(row.completed)
            payment_status = parse_payment_status(row.payment_status)
            enrollments.append(
                Enrollment(
                    enrollment_id=len(enrollments) + 1,
                    student_id=student_id,
                    session_id=session_id,
                    reg_date=row.reg_date,
                    completed=completed,
                    payment_status=payment_status,
                    exception=row.exception,
                )
            )

    return enrollments


def _select_course_by_name(courses: list[Course], name: str) -> Course:
    for course in courses:
        if course.course_name == name:
            return course
    raise ValueError(f"course={name} not found")
