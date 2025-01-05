from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from app.babies.models import (
    Baby,
    BabyCreate,
    Bath,
    BathCreate,
    DiaperChange,
    DiaperChangeCreate,
    Feeding,
    FeedingCreate,
    Measurement,
    MeasurementCreate,
    Medication,
    MedicationCreate,
    MedicationLogs,
    MedicationLogsCreate,
    Sleep,
    SleepCreate,
)
from app.database import SessionDep
from app.oauth2 import CurrentUserDep

router = APIRouter(prefix="/babies", tags=["Babies"])


def is_baby_owner(id: str, user: CurrentUserDep, session: SessionDep):
    baby = session.get(Baby, id)
    if not baby or baby.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found"
        )

    return baby


BabyOwnerDep = Annotated[Baby, Depends(is_baby_owner)]


def medication_owner(medication_id: str, baby: BabyOwnerDep, session: SessionDep):
    medication = session.get(Medication, medication_id)
    if not medication or medication.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found"
        )

    return medication


MedicationOwnerDep = Annotated[Medication, Depends(medication_owner)]


# Baby CRUD
@router.get("/", response_model=List[Baby])
def read_babies(
    user: CurrentUserDep,
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    babies = session.exec(
        select(Baby).where(Baby.user_id == user.id).offset(offset).limit(limit)
    ).all()
    return babies


@router.get("/{id}", response_model=Baby)
def read_baby(baby: BabyOwnerDep):
    return baby


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Baby)
def create_baby(baby: BabyCreate, session: SessionDep, user: CurrentUserDep):
    new_baby = Baby(**baby.model_dump(), user_id=user.id)
    valid_baby = Baby.model_validate(new_baby)
    session.add(valid_baby)
    session.commit()
    session.refresh(valid_baby)
    return valid_baby


# TODO: improve patch
@router.patch("/{id}", response_model=Baby)
def update_baby(baby: BabyCreate, existing_baby: BabyOwnerDep, session: SessionDep):
    existing_baby.birthdate = baby.birthdate
    existing_baby.name = baby.name

    Baby.model_validate(existing_baby, strict=True)

    session.add(existing_baby)
    session.commit()
    session.refresh(existing_baby)
    return existing_baby


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_baby(session: SessionDep, baby: BabyOwnerDep) -> None:
    session.delete(baby)
    session.commit()


# Diaper CRUD
@router.get("/{id}/diapers", response_model=List[DiaperChange])
def get_diapers(
    id: str,
    session: SessionDep,
    user: CurrentUserDep,
):
    current_baby = session.get(Baby, id)
    if not current_baby or current_baby.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Baby not found"
        )

    diapers = session.exec(select(DiaperChange).where(DiaperChange.baby_id == id)).all()
    return diapers


@router.post(
    "/{id}/diapers", status_code=status.HTTP_201_CREATED, response_model=DiaperChange
)
def add_diaper_change(
    diaper: DiaperChangeCreate,
    session: SessionDep,
    baby: BabyOwnerDep,
):
    new_diaper = DiaperChange(**diaper.model_dump(), baby_id=baby.id)
    valid_diaper = DiaperChange.model_validate(new_diaper)
    session.add(valid_diaper)
    session.commit()
    session.refresh(valid_diaper)
    return valid_diaper


@router.patch("/{id}/diapers/{diaper_id}", response_model=DiaperChange)
def update_diaper_change(
    diaper: DiaperChangeCreate,
    diaper_id: str,
    baby: BabyOwnerDep,
    session: SessionDep,
):
    existing_diaper = session.get(DiaperChange, diaper_id)
    if not existing_diaper or existing_diaper.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diaper change not found"
        )

    existing_diaper.time = diaper.time
    existing_diaper.pipi = diaper.pipi
    existing_diaper.poop = diaper.poop
    existing_diaper.used_cream = diaper.used_cream

    DiaperChange.model_validate(existing_diaper, strict=True)

    session.add(existing_diaper)
    session.commit()
    session.refresh(existing_diaper)
    return existing_diaper


@router.delete("/{id}/diapers/{diaper_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_diaper_change(session: SessionDep, diaper_id: str, baby: BabyOwnerDep):
    diaper = session.get(DiaperChange, diaper_id)
    if not diaper or diaper.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Diaper change not found"
        )

    session.delete(diaper)
    session.commit()


# Feeding CRUD
@router.get("/{id}/feedings", response_model=List[Feeding])
def get_feedings(baby: BabyOwnerDep, session: SessionDep):
    feedings = session.exec(select(Feeding).where(Feeding.baby_id == baby.id)).all()
    return feedings


@router.post(
    "/{id}/feedings", status_code=status.HTTP_201_CREATED, response_model=Feeding
)
def add_feeding(feeding: FeedingCreate, baby: BabyOwnerDep, session: SessionDep):
    new_feeding = Feeding(**feeding.model_dump(), baby_id=baby.id)
    valid_feeding = Feeding.model_validate(new_feeding)
    session.add(valid_feeding)
    session.commit()
    session.refresh(valid_feeding)
    return valid_feeding


@router.patch("/{id}/feedings/{feeding_id}", response_model=Feeding)
def update_feeding(
    feeding: FeedingCreate, feeding_id: str, baby: BabyOwnerDep, session: SessionDep
):
    existing_feeding = session.get(Feeding, feeding_id)
    if not existing_feeding or existing_feeding.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feeding not found"
        )

    existing_feeding.start_time = feeding.start_time
    existing_feeding.end_time = feeding.end_time
    existing_feeding.type = feeding.type
    existing_feeding.left_breast = feeding.left_breast
    existing_feeding.right_breast = feeding.right_breast

    Feeding.model_validate(existing_feeding, strict=True)

    session.add(existing_feeding)
    session.commit()
    session.refresh(existing_feeding)
    return existing_feeding


@router.delete("/{id}/feedings/{feeding_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feeding(session: SessionDep, feeding_id: str, baby: BabyOwnerDep):
    feeding = session.get(Feeding, feeding_id)
    if not feeding or feeding.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feeding not found"
        )

    session.delete(feeding)
    session.commit()


# Measurements CRUD
@router.get("/{id}/measurements", response_model=List[Measurement])
def get_measurements(baby: BabyOwnerDep, session: SessionDep):
    measurements = session.exec(
        select(Measurement).where(Measurement.baby_id == baby.id)
    ).all()
    return measurements


@router.post(
    "/{id}/measurements",
    status_code=status.HTTP_201_CREATED,
    response_model=Measurement,
)
def create_measurement(
    measurement: MeasurementCreate, baby: BabyOwnerDep, session: SessionDep
):
    new_measurement = Measurement(**measurement.model_dump(), baby_id=baby.id)
    valid_measurement = Measurement.model_validate(new_measurement)
    session.add(valid_measurement)
    session.commit()
    session.refresh(valid_measurement)
    return valid_measurement


@router.patch("/{id}/measurements/{measurement_id}", response_model=Measurement)
def update_measurement(
    measurement: MeasurementCreate,
    measurement_id: str,
    baby: BabyOwnerDep,
    session: SessionDep,
):
    existing_measurement = session.get(Measurement, measurement_id)
    if not existing_measurement or existing_measurement.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found"
        )

    existing_measurement.time = measurement.time
    existing_measurement.height = measurement.height
    existing_measurement.weight = measurement.weight

    Measurement.model_validate(existing_measurement, strict=True)

    session.add(existing_measurement)
    session.commit()
    session.refresh(existing_measurement)
    return existing_measurement


@router.delete(
    "/{id}/measurements/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_measurement(session: SessionDep, measurement_id: str, baby: BabyOwnerDep):
    measurement = session.get(Measurement, measurement_id)
    if not measurement or measurement.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Measurement not found"
        )

    session.delete(measurement)
    session.commit()


# Sleeps CRUD
@router.get("/{id}/sleeps", response_model=List[Sleep])
def get_sleeps(baby: BabyOwnerDep, session: SessionDep):
    sleeps = session.exec(select(Sleep).where(Sleep.baby_id == baby.id)).all()
    return sleeps


@router.post("/{id}/sleeps", status_code=status.HTTP_201_CREATED, response_model=Sleep)
def create_sleep(sleep: SleepCreate, baby: BabyOwnerDep, session: SessionDep):
    new_sleep = Sleep(**sleep.model_dump(), baby_id=baby.id)
    valid_sleep = Sleep.model_validate(new_sleep)
    session.add(valid_sleep)
    session.commit()
    session.refresh(valid_sleep)
    return valid_sleep


@router.patch("/{id}/sleeps/{sleep_id}", response_model=Sleep)
def update_sleep(
    sleep: SleepCreate, sleep_id: str, baby: BabyOwnerDep, session: SessionDep
):
    existing_sleep = session.get(Sleep, sleep_id)
    if not existing_sleep or existing_sleep.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sleep not found"
        )

    existing_sleep.start_time = sleep.start_time
    existing_sleep.end_time = sleep.end_time

    Sleep.model_validate(existing_sleep, strict=True)

    session.add(existing_sleep)
    session.commit()
    session.refresh(existing_sleep)
    return existing_sleep


@router.delete("/{id}/sleeps/{sleep_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sleep(session: SessionDep, sleep_id: str, baby: BabyOwnerDep):
    sleep = session.get(Sleep, sleep_id)
    if not sleep or sleep.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sleep not found"
        )

    session.delete(sleep)
    session.commit()


# Bath CRUD
@router.get("/{id}/baths", response_model=List[Bath])
def get_baths(baby: BabyOwnerDep, session: SessionDep):
    baths = session.exec(select(Bath).where(Bath.baby_id == baby.id)).all()
    return baths


@router.post("/{id}/baths", status_code=status.HTTP_201_CREATED, response_model=Bath)
def create_bath(bath: BathCreate, baby: BabyOwnerDep, session: SessionDep):
    new_bath = Bath(**bath.model_dump(), baby_id=baby.id)
    valid_bath = Bath.model_validate(new_bath)
    session.add(valid_bath)
    session.commit()
    session.refresh(valid_bath)
    return valid_bath


@router.patch("/{id}/baths/{bath_id}", response_model=Bath)
def update_bath(
    bath: BathCreate, bath_id: str, baby: BabyOwnerDep, session: SessionDep
):
    existing_bath = session.get(Bath, bath_id)
    if not existing_bath or existing_bath.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bath not found"
        )

    existing_bath.time = bath.time

    Bath.model_validate(existing_bath, strict=True)

    session.add(existing_bath)
    session.commit()
    session.refresh(existing_bath)
    return existing_bath


@router.delete("/{id}/baths/{bath_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bath(session: SessionDep, bath_id: str, baby: BabyOwnerDep):
    bath = session.get(Bath, bath_id)
    if not bath or bath.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bath not found"
        )

    session.delete(bath)
    session.commit()


# Medications CRUD
@router.get("/{id}/medications", response_model=List[Medication])
def get_medications(baby: BabyOwnerDep, session: SessionDep):
    medications = session.exec(
        select(Medication).where(Medication.baby_id == baby.id)
    ).all()
    return medications


@router.post(
    "/{id}/medications", status_code=status.HTTP_201_CREATED, response_model=Medication
)
def create_medication(
    medication: MedicationCreate, baby: BabyOwnerDep, session: SessionDep
):
    new_medication = Medication(**medication.model_dump(), baby_id=baby.id)
    valid_medication = Medication.model_validate(new_medication)
    session.add(valid_medication)
    session.commit()
    session.refresh(valid_medication)
    return valid_medication


@router.patch("/{id}/medications/{medication_id}", response_model=Medication)
def update_medication(
    medication: MedicationCreate,
    medication_id: str,
    baby: BabyOwnerDep,
    session: SessionDep,
):
    existing_medication = session.get(Medication, medication_id)
    if not existing_medication or existing_medication.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found"
        )

    existing_medication.name = medication.name
    existing_medication.dosage = medication.dosage
    existing_medication.description = medication.description
    existing_medication.is_active = medication.is_active
    existing_medication.is_vaccine = medication.is_vaccine

    Medication.model_validate(existing_medication, strict=True)

    session.add(existing_medication)
    session.commit()
    session.refresh(existing_medication)
    return existing_medication


@router.delete(
    "/{id}/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_medication(session: SessionDep, medication_id: str, baby: BabyOwnerDep):
    medication = session.get(Medication, medication_id)
    if not medication or medication.baby_id != baby.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found"
        )

    session.delete(medication)
    session.commit()


# Medication Logs CRUD
@router.get(
    "/{id}/medications/{medication_id}/logs", response_model=List[MedicationLogs]
)
def get_medication_logs(medication: MedicationOwnerDep, session: SessionDep):
    medication_logs = session.exec(
        select(MedicationLogs).where(MedicationLogs.medication_id == medication.id)
    ).all()
    return medication_logs


@router.post(
    "/{id}/medications/{medication_id}/logs",
    status_code=status.HTTP_201_CREATED,
    response_model=MedicationLogs,
)
def create_medication_log(
    medication_log: MedicationLogsCreate,
    medication: MedicationOwnerDep,
    session: SessionDep,
):
    new_medication_log = MedicationLogs(
        **medication_log.model_dump(), medication_id=medication.id
    )
    valid_medication_log = MedicationLogs.model_validate(new_medication_log)
    session.add(valid_medication_log)
    session.commit()
    session.refresh(valid_medication_log)
    return valid_medication_log


@router.patch(
    "/{id}/medications/{medication_id}/logs/{medication_log_id}",
    response_model=MedicationLogs,
)
def update_medication_log(
    medication_log: MedicationLogsCreate,
    medication_log_id: str,
    medication: MedicationOwnerDep,
    session: SessionDep,
):
    existing_medication_log = session.get(MedicationLogs, medication_log_id)
    if (
        not existing_medication_log
        or existing_medication_log.medication_id != medication.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medication log not found"
        )

    existing_medication_log.time = medication_log.time
    existing_medication_log.dosage = medication_log.dosage
    existing_medication_log.description = medication_log.description

    MedicationLogs.model_validate(existing_medication_log, strict=True)

    session.add(existing_medication_log)
    session.commit()
    session.refresh(existing_medication_log)
    return existing_medication_log


@router.delete(
    "/{id}/medications/{medication_id}/logs/{medication_log_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_medication_log(
    session: SessionDep, medication_log_id: str, medication: MedicationOwnerDep
):
    medication_log = session.get(MedicationLogs, medication_log_id)
    if not medication_log or medication_log.medication_id != medication.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Medication log not found"
        )

    session.delete(medication_log)
    session.commit()
