import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import event
from sqlmodel import Field, SQLModel

from app.database import TimestampMixin, update_timestamp


# Baby models
class BabyBase(SQLModel):
    birthdate: datetime
    name: str | None = Field(max_length=255)


class Baby(BabyBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")


class BabyCreate(BabyBase):
    pass


# Measurement models
class MeasurementBase(SQLModel):
    time: datetime | None = Field(default_factory=datetime.now)
    height: int | None  # in centimeters
    weight: int | None  # in grams


class Measurement(MeasurementBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    baby_id: uuid.UUID = Field(foreign_key="baby.id")


class MeasurementCreate(MeasurementBase):
    pass


# Diaper models
class DiaperChangeBase(SQLModel):
    time: datetime | None = Field(default_factory=datetime.now)
    pipi: bool
    poop: bool
    used_cream: bool = Field(default=False)


class DiaperChange(DiaperChangeBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    baby_id: uuid.UUID = Field(foreign_key="baby.id")


class DiaperChangeCreate(DiaperChangeBase):
    pass


# Feeding models
class FeedingType(str, Enum):
    BREAST = "breast"
    BOTTLE = "bottle"


class FeedingBase(SQLModel):
    start_time: datetime | None = Field(default_factory=datetime.now)
    end_time: datetime | None = Field(default=None)
    type: FeedingType
    left_breast: Optional[int] = Field(default=None)  # 1, 2, or NULL
    right_breast: Optional[int] = Field(default=None)  # 1, 2, or NULL


class Feeding(FeedingBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    baby_id: uuid.UUID = Field(foreign_key="baby.id")


class FeedingCreate(FeedingBase):
    pass


# Sleep models
class SleepBase(SQLModel):
    start_time: datetime | None = Field(default_factory=datetime.now)
    end_time: datetime | None = Field(default=None)


class Sleep(SleepBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    baby_id: uuid.UUID = Field(foreign_key="baby.id")


class SleepCreate(SleepBase):
    pass


# Bath models
class BathBase(SQLModel):
    time: datetime | None = Field(default_factory=datetime.now)


class Bath(BathBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    baby_id: uuid.UUID = Field(foreign_key="baby.id")


class BathCreate(BathBase):
    pass


# Medication models
class MedicationBase(SQLModel):
    name: str = Field(max_length=255)
    dosage: str
    description: str | None = Field(max_length=255, default=None)
    is_active: bool = Field(default=True)
    is_vaccine: bool = Field(default=False)


class Medication(MedicationBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    baby_id: uuid.UUID = Field(foreign_key="baby.id")


class MedicationCreate(MedicationBase):
    pass


class MedicationLogsBase(SQLModel):
    time: datetime | None = Field(default_factory=datetime.now)
    dosage: float | None = Field(default=1)
    description: str | None = Field(max_length=255, default=None)


class MedicationLogs(MedicationLogsBase, TimestampMixin, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    medication_id: uuid.UUID = Field(foreign_key="medication.id")


class MedicationLogsCreate(MedicationLogsBase):
    pass


event.listen(Baby, "before_update", update_timestamp)
event.listen(Measurement, "before_update", update_timestamp)
event.listen(DiaperChange, "before_update", update_timestamp)
event.listen(Feeding, "before_update", update_timestamp)
event.listen(Sleep, "before_update", update_timestamp)
event.listen(Bath, "before_update", update_timestamp)
event.listen(Medication, "before_update", update_timestamp)
event.listen(MedicationLogs, "before_update", update_timestamp)
