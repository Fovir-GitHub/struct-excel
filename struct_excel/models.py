from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from sqlmodel import Field, SQLModel


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CourseSessionMode(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"


class Sector(str, Enum):
    GOVERNMENT = "Government"
    PRIVATE = "Private"
    STUDENT = "Student"


class PaymentStatus(str, Enum):
    PAID = "PAID"
    PENDING = "PENDING"


class Student(SQLModel, table=True):
    student_id: int | None = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(unique=True, index=True)
    gender: Gender = Field(default=Gender.OTHER)
    it_background: bool
    experience_min_years: int = Field(default=None)
    experience_max_years: int = Field(default=None)
    sector: Sector = Field(default=Sector.STUDENT)
    supervisor_id: int | None = Field(
        default=None, foreign_key="supervisor.supervisor_id"
    )
    company: str
    job_title: str | None = Field(default=None)
    country: str
    phone: str


class Course(SQLModel, table=True):
    course_id: int | None = Field(default=None, primary_key=True)
    course_name: str


class CourseSession(SQLModel, table=True):
    session_id: int | None = Field(default=None, primary_key=True)
    course_id: int = Field(foreign_key="course.course_id")
    start_datetime: datetime
    end_datetime: datetime
    mode: CourseSessionMode = Field(default=CourseSessionMode.OFFLINE)
    duration: float = Field(default=0)


class Supervisor(SQLModel, table=True):
    supervisor_id: int | None = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(unique=True)


class Enrollment(SQLModel, table=True):
    enrollment_id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.student_id")
    session_id: int = Field(foreign_key="coursesession.session_id")
    reg_date: datetime
    completed: bool = Field(default=False)
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    exception: str | None = Field(default=None)


@dataclass
class RawRow:
    reg_date: datetime
    student_full_name: str
    student_email: str
    student_company: str
    student_job_title: str | None
    country: str
    exception: str | None
    phone: str
    course: str
    gender: str
    sector: str
    supervisor_name: str | None
    supervisor_email: str | None
    it_background: str | None
    experience: str | None
    completed: str | None
    payment_status: str | None


@dataclass
class CourseParseResult:
    datetime_range: list[tuple[datetime, datetime]]
    mode: CourseSessionMode
    course_name: str
    duration: float
