Database Schema for Newborn Baby Routine Tracking App

Tables:

1. users

id: Primary key (UUID or auto-increment integer)

email: Email address of the parent/guardian (unique, string)

password: Hashed password (string)

created_at: Timestamp of user registration

updated_at: Timestamp of last user update

2. babies

id: Primary key (UUID or auto-increment integer)

user_id: Foreign key referencing users.id

birthdate: Date of birth of the baby (date)

created_at: Timestamp of baby registration

updated_at: Timestamp of last baby update

3. diaper_changes

id: Primary key (UUID or auto-increment integer)

baby_id: Foreign key referencing babies.id

time: Timestamp of diaper change

pipi: Boolean indicating if it was urine

poop: Boolean indicating if it was stool

4. feeding

id: Primary key (UUID or auto-increment integer)

baby_id: Foreign key referencing babies.id

start_time: Timestamp when feeding started

end_time: Timestamp when feeding ended

type: Enum or string ("breast" or "bottle")

left_breast: Integer or NULL, values 1 (used first), 2 (used second), or NULL (not used).

right_breast: Integer or NULL, values 1 (used first), 2 (used second), or NULL (not used).

5. sleep

id: Primary key (UUID or auto-increment integer)

baby_id: Foreign key referencing babies.id

start_time: Timestamp when sleep started

end_time: Timestamp when sleep ended

6. baths

id: Primary key (UUID or auto-increment integer)

baby_id: Foreign key referencing babies.id

time: Timestamp of bath

7. medications

id: Primary key (UUID or auto-increment integer)

baby_id: Foreign key referencing babies.id

name: Name of the medication (string)

dosage: Dosage details (string)

description: Additional information (string)

category: Boolean indicating if it is a vaccine

8. medication_logs

id: Primary key (UUID or auto-increment integer)

medication_id: Foreign key referencing medications.id

time_taken: Timestamp when the medication was administered

Design Rationale:

Minimal Data Collection: Only essential personal information is collected (email, password).

Normalization: Each type of event (e.g., diaper changes, feeding) is stored in its own table to ensure data integrity and prevent redundancy.

Scalability: The schema supports multiple babies per user and multiple event entries for each baby.

Timestamp Fields: Added created_at and updated_at for auditing purposes in users and babies tables.

Medication Logs: Separate medication_logs table to track specific instances of medication administration, ensuring clarity and scalability.
