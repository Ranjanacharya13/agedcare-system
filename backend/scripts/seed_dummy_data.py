"""Seed the Supabase tables with ~10 realistic, imaginary rows per resource."""

import asyncio
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID

from backend.db.supabase_client import close_supabase_connection, connect_to_supabase, get_supabase
from backend.models.appointment import Appointment, AppointmentStatus
from backend.models.assistance import AssistanceLevel, ResidentAssistance
from backend.models.behaviour import ResidentBehaviour
from backend.models.bowel_chart import ResidentBowelChart
from backend.models.complaint import ComplaintFeedback, ComplaintStatus
from backend.models.employee import Employee, EmployeeRole, EmploymentStatus
from backend.models.employee_availability import EmployeeAvailability
from backend.models.employee_contract import EmployeeContract
from backend.models.employee_leave import EmployeeLeave, LeaveStatus
from backend.models.employee_payroll_record import EmployeePayrollRecord, PayrollStatus
from backend.models.employee_performance import EmployeePerformance
from backend.models.employee_qualification import EmployeeQualification
from backend.models.employee_registration import EmployeeRegistration
from backend.models.employee_shift import EmployeeShift, ShiftStatus
from backend.models.employee_supervision import EmployeeSupervision
from backend.models.employee_time_entry import EmployeeTimeEntry
from backend.models.fall_risk import ResidentFallRisk, RiskLevel
from backend.models.incident import IncidentSeverity, IncidentStatus, ResidentIncident
from backend.models.medical_history import ResidentMedicalHistory
from backend.models.medical_inventory import ResidentMedicalInventory
from backend.models.medication import ResidentMedication
from backend.models.resident import CognitiveStatus, EmergencyContact, Resident
from backend.models.sleep_chart import ResidentSleepChart
from backend.repositories.appointment_repository import AppointmentRepository
from backend.repositories.base import SupabaseRepository
from backend.repositories.complaint_repository import ComplaintRepository
from backend.repositories.employee_repository import EmployeeRepository
from backend.repositories.resident_repository import ResidentRepository

UTC = timezone.utc


def _d(year: int, month: int, day: int) -> date:
    return date(year, month, day)


def _dt(year: int, month: int, day: int, hour: int = 9, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


async def _insert_all(repo, label: str, records: list) -> list[UUID]:
    ids: list[UUID] = []
    for i, record in enumerate(records, start=1):
        try:
            created = await repo.create(record)
            ids.append(created.id)
        except Exception as exc:  # noqa: BLE001 - report and keep seeding other resources
            print(f"  [{label}] row {i} FAILED: {exc}")
    print(f"Seeded {len(ids)}/{len(records)} {label}")
    return ids


async def seed_residents(client) -> list[UUID]:
    repo = ResidentRepository(client)
    names = [
        ("Margaret", "Thompson", "Female"),
        ("Harold", "Nguyen", "Male"),
        ("Beryl", "O'Connor", "Female"),
        ("Frank", "Kowalski", "Male"),
        ("Doris", "Patel", "Female"),
        ("Walter", "Higgins", "Male"),
        ("Shirley", "Wallace", "Female"),
        ("Raymond", "Singh", "Male"),
        ("Audrey", "Fitzgerald", "Female"),
        ("Bruce", "MacKenzie", "Male"),
    ]
    dobs = [
        _d(1938, 3, 14), _d(1935, 11, 2), _d(1930, 1, 22), _d(1942, 7, 30), _d(1933, 9, 9),
        _d(1929, 12, 25), _d(1940, 4, 18), _d(1936, 6, 11), _d(1931, 10, 5), _d(1937, 2, 28),
    ]
    cognitive = list(CognitiveStatus)  # 4 values, cycle across 10
    rooms = ["101A", "102B", "103A", "104C", "105B", "106A", "107C", "108B", "109A", "110C"]
    admissions = [
        _d(2020, 5, 1), _d(2019, 8, 15), _d(2021, 2, 10), _d(2018, 11, 20), _d(2022, 1, 5),
        _d(2017, 6, 3), _d(2023, 3, 12), _d(2020, 9, 27), _d(2019, 4, 8), _d(2016, 10, 30),
    ]
    contacts = [
        EmergencyContact(name="Susan Thompson", relationship="Daughter", phone="0412 345 678", email="susan.t@example.com"),
        EmergencyContact(name="Kevin Nguyen", relationship="Son", phone="0423 456 789", email=None),
        None,
        EmergencyContact(name="Anna Kowalski", relationship="Wife", phone="0434 567 890", email="anna.k@example.com"),
        EmergencyContact(name="Priya Patel", relationship="Daughter", phone="0445 678 901", email="priya.p@example.com"),
        EmergencyContact(name="Ian Higgins", relationship="Son", phone="0456 789 012", email=None),
        EmergencyContact(name="Karen Wallace", relationship="Niece", phone="0467 890 123", email="karen.w@example.com"),
        None,
        EmergencyContact(name="Colin Fitzgerald", relationship="Son", phone="0478 901 234", email="colin.f@example.com"),
        EmergencyContact(name="Fiona MacKenzie", relationship="Daughter", phone="0489 012 345", email="fiona.m@example.com"),
    ]
    active = [True, True, True, False, True, True, True, True, True, False]

    records = [
        Resident(
            first_name=n[0], last_name=n[1], dob=dobs[i], gender=n[2],
            cognitive_status=cognitive[i % len(cognitive)], room_number=rooms[i],
            admission_date=admissions[i], emergency_contact=contacts[i], active=active[i],
        )
        for i, n in enumerate(names)
    ]
    return await _insert_all(repo, "residents", records)


async def seed_employees(client) -> list[UUID]:
    repo = EmployeeRepository(client)
    rows = [
        ("Emily", "Carter", EmployeeRole.CARE_PLANNER, EmploymentStatus.FULL_TIME, _d(2018, 2, 5), None, True),
        ("Jason", "Reid", EmployeeRole.CARE_COORDINATOR, EmploymentStatus.FULL_TIME, _d(2016, 6, 19), None, True),
        ("Priya", "Sharma", EmployeeRole.REGISTERED_NURSE, EmploymentStatus.FULL_TIME, _d(2015, 9, 1), None, True),
        ("Liam", "O'Brien", EmployeeRole.REGISTERED_NURSE, EmploymentStatus.PART_TIME, _d(2021, 3, 22), None, True),
        ("Chloe", "Bennett", EmployeeRole.KITCHEN_STAFF, EmploymentStatus.CASUAL, _d(2022, 7, 11), None, True),
        ("Marcus", "Webb", EmployeeRole.LAUNDRY_STAFF, EmploymentStatus.CASUAL, _d(2019, 1, 14), _d(2024, 5, 30), False),
        ("Natalie", "Dixon", EmployeeRole.ADMINISTRATOR, EmploymentStatus.FULL_TIME, _d(2017, 11, 8), None, True),
        ("Samuel", "Grant", EmployeeRole.MANAGER, EmploymentStatus.FULL_TIME, _d(2014, 4, 2), None, True),
        ("Grace", "Ferreira", EmployeeRole.CARE_COORDINATOR, EmploymentStatus.PART_TIME, _d(2020, 10, 26), None, True),
        ("Ethan", "Wu", EmployeeRole.REGISTERED_NURSE, EmploymentStatus.AGENCY, _d(2023, 8, 17), None, True),
    ]
    records = [
        Employee(
            first_name=r[0], last_name=r[1],
            email=f"{r[0].lower()}.{r[1].lower().replace(chr(39), '')}@agedcare.example.com",
            phone=f"04{10 + i:02d} {100 + i * 11:03d} {200 + i * 7:03d}",
            role=r[2], employment_status=r[3], hire_date=r[4], termination_date=r[5], active=r[6],
        )
        for i, r in enumerate(rows)
    ]
    return await _insert_all(repo, "employees", records)


async def seed_complaints(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = ComplaintRepository(client)
    categories = [
        "Care Quality", "Food & Catering", "Communication", "Cleanliness", "Billing",
        "Staff Conduct", "Medication", "Facilities", "Activities", "Other",
    ]
    descriptions = [
        "Family felt call bell response times were too slow overnight.",
        "Meal was cold and did not match the dietary plan on file.",
        "Weekly care update phone call was missed for two weeks running.",
        "Bathroom in room 104C had not been cleaned before a family visit.",
        "Invoice included a service that was never provided.",
        "A staff member spoke to the resident in a dismissive tone.",
        "Evening medication was given almost two hours late.",
        "Handrail in the corridor near the dining hall is loose.",
        "Resident was excluded from the music therapy session without explanation.",
        "General feedback about the new visitor sign-in process.",
    ]
    relationships = ["Daughter", "Son", "Spouse", "Friend", "Sister", "Son", "Daughter", "Nephew", "Anonymous", "Daughter"]
    is_anonymous = [False, False, False, False, False, False, False, False, True, False]
    submitted_names = [
        "Susan Thompson", "Kevin Nguyen", "Anna Kowalski", "Priya Patel", "Ian Higgins",
        "Karen Wallace", "Colin Fitzgerald", "David Singh", "Anonymous", "Fiona MacKenzie",
    ]
    statuses = list(ComplaintStatus)

    records = []
    for i in range(10):
        records.append(ComplaintFeedback(
            resident_id=residents[i % len(residents)],
            employee_id=employees[i % len(employees)] if categories[i] == "Staff Conduct" else None,
            category=categories[i],
            description=descriptions[i],
            submitted_by_name=submitted_names[i],
            submitted_by_relationship=None if is_anonymous[i] else relationships[i],
            submitted_by_contact=None if is_anonymous[i] else f"04{50 + i:02d} 111 {300 + i:03d}",
            is_anonymous=is_anonymous[i],
            status=statuses[i % len(statuses)],
            assigned_to=None if statuses[i % len(statuses)] == ComplaintStatus.OPEN else employees[(i + 2) % len(employees)],
        ))
    return await _insert_all(repo, "complaints", records)


async def seed_appointments(client, employees: list[UUID]) -> list[UUID]:
    repo = AppointmentRepository(client)
    names = [
        "Barbara Ellis", "George Okafor", "Linda Marsh", "Peter Costa", "Yvonne Blake",
        "Robert Chan", "Michelle Doyle", "Tony Russo", "Sandra Lopez", "Nigel Foster",
    ]
    types = ["Facility Tour", "Consultation", "Admission Enquiry", "Care Assessment"]
    statuses = list(AppointmentStatus)
    messages = [
        "Looking to tour the facility for my mother next month.",
        "Would like to discuss respite care options.",
        "Interested in permanent admission for my father, cognitive care needed.",
        "Requesting a home-based care assessment before deciding.",
        "Following up on the brochure I received at the expo.",
        "Need wheelchair-accessible tour time slots.",
        "Would like an interpreter present for the consultation.",
        "Asking about waitlist times for a single room.",
        "Enquiring on behalf of a client at my aged-care advisory firm.",
        "Just some general questions about pricing and packages.",
    ]

    records = []
    for i in range(10):
        status = statuses[i % len(statuses)]
        scheduled = status in (AppointmentStatus.CONFIRMED, AppointmentStatus.COMPLETED)
        records.append(Appointment(
            full_name=names[i],
            email=f"{names[i].split()[0].lower()}.{names[i].split()[1].lower()}@example.com",
            phone=f"04{60 + i:02d} 222 {400 + i:03d}",
            appointment_type=types[i % len(types)],
            preferred_date=_d(2026, 8, 1) + timedelta(days=i * 3),
            preferred_time=time(9 + (i % 6), 30 if i % 2 else 0),
            message=messages[i],
            status=status,
            scheduled_at=_dt(2026, 8, 1 + i, 10, 0) if scheduled else None,
            handled_by=employees[i % len(employees)] if scheduled else None,
            admin_notes="Confirmed by phone." if status == AppointmentStatus.CONFIRMED else None,
        ))
    return await _insert_all(repo, "appointments", records)


async def seed_medical_history(client, residents: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_medical_history", ResidentMedicalHistory)
    diagnoses = [
        "Type 2 Diabetes", "Alzheimer's Disease", "Parkinson's Disease", "Chronic Heart Failure",
        "Osteoarthritis", "COPD", "Vascular Dementia", "Hypertension", "Rheumatoid Arthritis", "Stroke (2021)",
    ]
    allergies = [
        "Penicillin", "None known", "Shellfish", "Sulfa drugs", "None known",
        "Latex", "Peanuts", "None known", "Aspirin", "None known",
    ]
    chronic = [
        "Diabetes, hypertension", "Dementia, mobility decline", "Parkinson's, tremor", "Heart failure, oedema",
        "Arthritis, chronic pain", "COPD, breathlessness", "Dementia, wandering risk", "Hypertension, high cholesterol",
        "Rheumatoid arthritis", "Post-stroke, left-side weakness",
    ]
    surgeries = [
        "Hip replacement (2015)", None, "Deep brain stimulation (2019)", "Coronary bypass (2010)",
        "Knee replacement (2018)", None, None, "Cataract surgery (2020)", "Hand surgery (2016)", "Carotid endarterectomy (2021)",
    ]
    doctors = [
        "Dr. Alan Reeves", "Dr. Fiona Marsh", "Dr. Simon Wu", "Dr. Kate Brennan", "Dr. Alan Reeves",
        "Dr. Priya Anand", "Dr. Fiona Marsh", "Dr. Simon Wu", "Dr. Kate Brennan", "Dr. Priya Anand",
    ]
    notes = [
        "Reviewed quarterly by GP.", "Family present at last review.", "Stable on current medication.",
        "Monitor fluid intake closely.", "Pain managed with physio.", "Oxygen saturation checked daily.",
        "High fall risk noted.", "Blood pressure checked weekly.", "Flare-ups managed with NSAIDs.",
        "Ongoing physiotherapy for mobility.",
    ]

    records = [
        ResidentMedicalHistory(
            resident_id=residents[i], diagnosis=diagnoses[i], allergies=allergies[i],
            chronic_conditions=chronic[i], surgeries=surgeries[i], doctor_name=doctors[i], notes=notes[i],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "medical-history", records)


async def seed_behaviour(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_behaviour", ResidentBehaviour)
    behaviours = [
        "Agitation before meals", "Wandering at night", "Verbal outburst", "Refusing personal care",
        "Repetitive questioning", "Withdrawal from activities", "Crying spells", "Resistance to bathing",
        "Calling out for family", "Sundowning confusion",
    ]
    triggers = [
        "Hunger", "Unfamiliar noise", "Denied request", "Fear of falling", "Short-term memory loss",
        "Fatigue", "Missing a family visit", "Cold water temperature", "Loneliness", "End of daylight",
    ]
    interventions = [
        "Offered a snack early", "Redirected to lounge with music", "Calm reassurance, stepped away",
        "Explained each step before starting", "Answered patiently, redirected to activity",
        "Encouraged rest before dinner", "Called family on speakerphone", "Warmed water, explained process",
        "Sat with resident for ten minutes", "Dimmed lights, played familiar music",
    ]
    outcomes = [
        "Settled within 10 minutes", "Returned to bed", "Calmed down", "Accepted care after reassurance",
        "Distracted successfully", "Napped for an hour", "Comforted, smiled", "Completed bathing calmly",
        "Settled after call", "Settled by 7pm",
    ]

    records = [
        ResidentBehaviour(
            resident_id=residents[i], behaviour=behaviours[i], trigger=triggers[i],
            intervention=interventions[i], outcome=outcomes[i], recorded_by=employees[i % len(employees)],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "behaviour", records)


async def seed_medications(client, residents: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_medications", ResidentMedication)
    meds = [
        ("Metformin", "500mg", "Twice daily", "Oral"),
        ("Donepezil", "5mg", "Once daily", "Oral"),
        ("Levodopa", "100mg", "Three times daily", "Oral"),
        ("Furosemide", "40mg", "Once daily", "Oral"),
        ("Paracetamol", "500mg", "As needed", "Oral"),
        ("Salbutamol", "100mcg", "As needed", "Inhaled"),
        ("Memantine", "10mg", "Once daily", "Oral"),
        ("Amlodipine", "5mg", "Once daily", "Oral"),
        ("Methotrexate", "10mg", "Weekly", "Oral"),
        ("Clopidogrel", "75mg", "Once daily", "Oral"),
    ]
    prescribers = [
        "Dr. Alan Reeves", "Dr. Fiona Marsh", "Dr. Simon Wu", "Dr. Kate Brennan", "Dr. Alan Reeves",
        "Dr. Priya Anand", "Dr. Fiona Marsh", "Dr. Simon Wu", "Dr. Kate Brennan", "Dr. Priya Anand",
    ]
    active = [True, True, True, True, False, True, True, True, True, True]

    records = [
        ResidentMedication(
            resident_id=residents[i], medication_name=meds[i][0], dosage=meds[i][1],
            frequency=meds[i][2], route=meds[i][3], prescribed_by=prescribers[i],
            start_date=_d(2023, 1, 1) + timedelta(days=i * 20),
            end_date=_d(2023, 6, 1) if not active[i] else None,
            active=active[i],
            notes="Review at next GP visit." if i % 3 == 0 else None,
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "medications", records)


async def seed_bowel_chart(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_bowel_chart", ResidentBowelChart)
    types = ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6", "Type 7", "Type 3", "Type 4", "Type 2"]
    consistency = ["Hard", "Hard", "Normal", "Normal", "Soft", "Loose", "Watery", "Normal", "Normal", "Hard"]
    notes = [
        "No discomfort reported", None, "Routine", None, "Increased fibre in diet", "Monitor hydration",
        None, "Routine", None, "Discussed with GP",
    ]

    records = [
        ResidentBowelChart(
            resident_id=residents[i], bowel_type=types[i], consistency=consistency[i],
            notes=notes[i], recorded_by=employees[(i + 1) % len(employees)],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "bowel-chart", records)


async def seed_sleep_chart(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_sleep_chart", ResidentSleepChart)
    disturbances = [
        None, "Woke twice for toileting", "Restless, called out", None, "Woke early, anxious",
        None, "Coughing fit at 2am", None, "Woke due to pain", "Nightmares reported",
    ]

    records = []
    for i in range(10):
        start = time(21, 0) if i % 2 == 0 else time(21, 30)
        wake = time(6, 30) if i % 2 == 0 else time(7, 0)
        records.append(ResidentSleepChart(
            resident_id=residents[i], sleep_date=_d(2026, 7, 1) + timedelta(days=i),
            sleep_start=start, wake_time=wake, total_hours=8.0 if i % 2 == 0 else 7.5,
            disturbances=disturbances[i], recorded_by=employees[(i + 2) % len(employees)],
        ))
    return await _insert_all(repo, "sleep-chart", records)


async def seed_fall_risk(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_fall_risk", ResidentFallRisk)
    levels = list(RiskLevel)
    interventions = [
        "Bed alarm activated, non-slip mats", "Regular toileting schedule", "Physiotherapy referral",
        "Hip protectors issued", "Low bed with mat", "Vision check scheduled", "Walking frame provided",
        "Increased supervision at night", "Footwear review", "Medication review for sedatives",
    ]

    records = [
        ResidentFallRisk(
            resident_id=residents[i], risk_level=levels[i % len(levels)],
            assessment_date=_d(2026, 6, 1) + timedelta(days=i * 5),
            assessed_by=employees[i % len(employees)],
            interventions=interventions[i],
            notes="Reassess in 3 months" if i % 2 == 0 else None,
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "fall-risk", records)


async def seed_assistance(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_assistance", ResidentAssistance)
    levels = list(AssistanceLevel)
    mobility = [
        "Walks independently", "Uses walking frame", "Wheelchair-bound", "Requires hoist for transfers",
        "Walks with one-person support", "Independent with cane", "Bedbound, full assistance",
        "Uses walking frame", "Independent", "Requires two-person transfer",
    ]

    records = [
        ResidentAssistance(
            resident_id=residents[i], assistance_level=levels[i % len(levels)], mobility=mobility[i],
            transfer_notes="Use gait belt" if levels[i % len(levels)] != AssistanceLevel.INDEPENDENT else None,
            updated_by=employees[(i + 3) % len(employees)],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "assistance", records)


async def seed_medical_inventory(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_medical_inventory", ResidentMedicalInventory)
    items = [
        ("Paracetamol 500mg", 60, "tablets"), ("Incontinence pads", 40, "units"), ("Wound dressings", 15, "packs"),
        ("Insulin pen", 3, "units"), ("Compression stockings", 4, "pairs"), ("Saline solution", 6, "bottles"),
        ("Nutritional supplement drink", 24, "cartons"), ("Barrier cream", 5, "tubes"), ("Thickener powder", 8, "tubs"),
        ("Blood glucose test strips", 100, "strips"),
    ]

    records = [
        ResidentMedicalInventory(
            resident_id=residents[i], item_name=items[i][0], quantity=items[i][1], unit=items[i][2],
            expiry_date=_d(2027, 1, 1) + timedelta(days=i * 30), notes=None if i % 2 else "Reorder when below 10%",
            added_by=employees[i % len(employees)],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "medical-inventory", records)


async def seed_incidents(client, residents: list[UUID], employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "resident_incidents", ResidentIncident)
    types = [
        "Fall", "Medication Error", "Skin Tear", "Behavioural Incident", "Choking",
        "Elopement Attempt", "Verbal Altercation", "Equipment Failure", "Missed Medication", "Unexplained Bruising",
    ]
    severities = list(IncidentSeverity)
    statuses = list(IncidentStatus)
    descriptions = [
        "Resident found on floor beside bed, no visible injury.", "Wrong dosage of Furosemide administered.",
        "Skin tear on forearm during transfer.", "Resident became agitated during dinner service.",
        "Resident coughed while eating, cleared airway unaided.", "Resident found near exit door at 4am.",
        "Verbal dispute between two residents in the lounge.", "Hoist stopped working mid-transfer.",
        "Evening dose of Metformin not administered due to stock shortage.", "Bruising noted on upper arm, cause unknown.",
    ]
    locations = [
        "Room 101A", "Room 102B medication room", "Room 103A", "Dining hall", "Dining hall",
        "Main corridor near exit", "Lounge room", "Room 104C", "Medication room", "Room 105B",
    ]

    records = []
    for i in range(10):
        severity = severities[i % len(severities)]
        reportable = severity in (IncidentSeverity.HIGH, IncidentSeverity.CRITICAL)
        records.append(ResidentIncident(
            resident_id=residents[i], incident_type=types[i], severity=severity,
            description=descriptions[i], occurred_at=_dt(2026, 6, 1 + i, 14, 15),
            location=locations[i], reported_by=employees[i % len(employees)],
            witnesses="None" if i % 2 == 0 else "Two staff members present",
            immediate_action="First aid administered, GP notified" if reportable else "Monitored, documented",
            is_sirs_reportable=reportable,
            sirs_notified_at=_dt(2026, 6, 1 + i, 16, 0) if reportable else None,
            sirs_reference_number=f"SIRS-2026-{1000 + i}" if reportable else None,
            status=statuses[i % len(statuses)],
            outcome="Resolved, care plan updated" if statuses[i % len(statuses)] == IncidentStatus.CLOSED else None,
        ))
    return await _insert_all(repo, "incidents", records)


async def seed_supervision(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_supervision", EmployeeSupervision, parent_field="employee_id")
    discussions = [
        "Discussed workload and rostering preferences.", "Reviewed recent medication administration audit.",
        "Career development and further study options.", "Feedback on teamwork during recent incident.",
        "Discussed client feedback from families.", "Reviewed punctuality and attendance.",
        "Wellbeing check-in and stress management.", "Discussed leadership training opportunities.",
        "Reviewed documentation quality.", "Annual goal-setting discussion.",
    ]
    actions = [
        "Adjust roster to reduce back-to-back doubles", "Complete refresher medication training",
        "Enrol in Diploma of Nursing bridging course", "Attend team communication workshop",
        "Follow up with family directly next visit", "No action required", "Reduced shift load for one month",
        "Nominate for supervisor shadowing program", "Weekly documentation spot-check for a month", "Set Q3 performance goals",
    ]

    records = [
        EmployeeSupervision(
            employee_id=employees[i], supervisor=employees[(i + 3) % len(employees)],
            supervision_date=_d(2026, 5, 1) + timedelta(days=i * 7), discussion=discussions[i],
            action_items=actions[i], follow_up_date=_d(2026, 8, 1) + timedelta(days=i * 7),
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "supervision", records)


async def seed_registration(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_registration", EmployeeRegistration, parent_field="employee_id")
    types = [
        "AHPRA Nursing Registration", "National Police Check", "Working With Vulnerable People Check",
        "First Aid Certificate", "Food Safety Supervisor Certificate", "AHPRA Nursing Registration",
        "National Police Check", "Working With Vulnerable People Check", "First Aid Certificate", "National Police Check",
    ]
    authorities = [
        "AHPRA", "Australian Federal Police", "Dept. of Communities", "St John Ambulance", "Food Standards Australia",
        "AHPRA", "Australian Federal Police", "Dept. of Communities", "St John Ambulance", "Australian Federal Police",
    ]
    verified = [True, True, False, True, True, True, False, True, True, False]

    records = [
        EmployeeRegistration(
            employee_id=employees[i], registration_type=types[i],
            registration_number=f"REG-{2026}-{500 + i}", issuing_authority=authorities[i],
            issue_date=_d(2023, 1, 1) + timedelta(days=i * 40),
            expiry_date=_d(2027, 1, 1) + timedelta(days=i * 40), verified=verified[i],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "registration", records)


async def seed_qualifications(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_qualifications", EmployeeQualification, parent_field="employee_id")
    names = [
        "Certificate III in Individual Support", "Diploma of Nursing", "Bachelor of Nursing",
        "Certificate IV in Ageing Support", "Food Safety Certificate", "Diploma of Community Services",
        "Bachelor of Business (Health Management)", "Certificate III in Commercial Cookery",
        "First Aid & CPR Certificate", "Diploma of Leadership and Management",
    ]
    institutions = [
        "TAFE NSW", "TAFE Queensland", "University of Sydney", "TAFE Victoria", "William Angliss Institute",
        "TAFE NSW", "RMIT University", "Box Hill Institute", "St John Ambulance", "Chisholm Institute",
    ]
    expiring = [False, False, False, False, True, False, False, True, True, False]

    records = [
        EmployeeQualification(
            employee_id=employees[i], qualification_name=names[i], institution=institutions[i],
            completion_date=_d(2018, 1, 1) + timedelta(days=i * 200),
            expiry_date=_d(2027, 1, 1) + timedelta(days=i * 30) if expiring[i] else None,
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "qualifications", records)


async def seed_performance(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_performance", EmployeePerformance, parent_field="employee_id")
    ratings = [3, 4, 5, 2, 4, 3, 5, 4, 1, 5]
    strengths = [
        "Reliable and punctual", "Excellent resident rapport", "Strong clinical skills", "Good team player",
        "Great attention to detail", "Calm under pressure", "Proactive problem solver", "Mentors junior staff",
        "Needs improvement across the board", "Outstanding leadership",
    ]
    improvements = [
        "Documentation timeliness", "Delegation skills", None, "Time management", "Confidence in escalation",
        "Communication with families", None, "Delegation to junior staff", "Attendance, punctuality, communication",
        None,
    ]
    goals = [
        "Complete medication competency", "Take on shift-lead role", "Mentor two graduate nurses",
        "Improve incident report turnaround", "Lead a care-planning session", "Complete dementia care training",
        "Apply for coordinator role", "Complete leadership course", "Performance improvement plan", "Support recruitment panel",
    ]

    records = [
        EmployeePerformance(
            employee_id=employees[i], reviewer=employees[(i + 2) % len(employees)],
            review_date=_d(2026, 4, 1) + timedelta(days=i * 10), overall_rating=ratings[i],
            strengths=strengths[i], improvements=improvements[i], goals=goals[i],
            next_review=_d(2026, 10, 1) + timedelta(days=i * 10),
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "performance", records)


async def seed_leave(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_leave", EmployeeLeave, parent_field="employee_id")
    types = [
        "Annual Leave", "Sick Leave", "Personal Leave", "Long Service Leave", "Unpaid Leave",
        "Annual Leave", "Sick Leave", "Personal Leave", "Annual Leave", "Long Service Leave",
    ]
    # LeaveStatus has no model default -> include one None to show the field is genuinely optional.
    statuses = [
        LeaveStatus.APPROVED, LeaveStatus.APPROVED, LeaveStatus.PENDING, LeaveStatus.APPROVED, LeaveStatus.REJECTED,
        LeaveStatus.CANCELLED, LeaveStatus.PENDING, LeaveStatus.APPROVED, None, LeaveStatus.APPROVED,
    ]

    records = []
    for i in range(10):
        status = statuses[i]
        approved = employees[(i + 1) % len(employees)] if status == LeaveStatus.APPROVED else None
        records.append(EmployeeLeave(
            employee_id=employees[i], leave_type=types[i],
            start_date=_d(2026, 7, 1) + timedelta(days=i * 6),
            end_date=_d(2026, 7, 5) + timedelta(days=i * 6),
            status=status, approved_by=approved,
            notes="Cover arranged with casual pool" if status == LeaveStatus.APPROVED else None,
        ))
    return await _insert_all(repo, "leave", records)


async def seed_contracts(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_contracts", EmployeeContract, parent_field="employee_id")
    types = [
        "Permanent Full-Time", "Permanent Full-Time", "Permanent Full-Time", "Permanent Part-Time", "Casual",
        "Casual", "Permanent Full-Time", "Permanent Full-Time", "Permanent Part-Time", "Agency Contract",
    ]
    hours = [38.0, 38.0, 38.0, 24.0, 0.0, 0.0, 38.0, 38.0, 24.0, 38.0]
    rates = [32.50, 34.00, 42.75, 41.00, 29.50, 27.80, 38.20, 55.00, 34.00, 48.00]
    ended = [False, False, False, False, False, True, False, False, False, False]

    records = [
        EmployeeContract(
            employee_id=employees[i], contract_type=types[i], contracted_hours=hours[i], hourly_rate=rates[i],
            start_date=_d(2018, 1, 1) + timedelta(days=i * 90),
            end_date=_d(2024, 6, 1) if ended[i] else None,
            annual_leave_hours=152.0 if hours[i] > 0 else 0.0,
            sick_leave_hours=76.0 if hours[i] > 0 else 0.0,
            notes="Reviewed annually" if i % 2 == 0 else None,
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "contracts", records)


async def seed_availability(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_availability", EmployeeAvailability, parent_field="employee_id")
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Wednesday", "Friday"]
    available = [True, True, True, True, True, False, False, True, True, False]

    records = [
        EmployeeAvailability(
            employee_id=employees[i % len(employees)], weekday=weekdays[i],
            start_time=time(7, 0) if available[i] else None,
            end_time=time(15, 0) if available[i] else None,
            available=available[i],
        )
        for i in range(10)
    ]
    return await _insert_all(repo, "availability", records)


async def seed_shifts(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_shifts", EmployeeShift, parent_field="employee_id")
    statuses = list(ShiftStatus)
    roles = ["Morning Care", "Afternoon Care", "Night Care", "Kitchen", "Laundry", "Admin", "Nursing", "Nursing", "Care Coordination", "Nursing"]
    locations = ["Wing A", "Wing B", "Wing A", "Kitchen", "Laundry Room", "Front Office", "Wing B", "Wing A", "Wing B", "Wing A"]

    records = []
    for i in range(10):
        start = _dt(2026, 7, 20 + i, 7, 0)
        end = start + timedelta(hours=8)
        records.append(EmployeeShift(
            employee_id=employees[i], shift_start=start, shift_end=end, role=roles[i],
            location=locations[i], status=statuses[i % len(statuses)],
            notes="Double-booked, confirm cover" if statuses[i % len(statuses)] == ShiftStatus.NO_SHOW else None,
        ))
    return await _insert_all(repo, "shifts", records)


async def seed_time_entries(client, employees: list[UUID], shifts: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_time_entries", EmployeeTimeEntry, parent_field="employee_id")
    records = []
    for i in range(10):
        clock_in = _dt(2026, 7, 20 + i, 7, 3)
        still_clocked_in = i == 9
        records.append(EmployeeTimeEntry(
            employee_id=employees[i], shift_id=shifts[i] if i < len(shifts) else None,
            clock_in=clock_in,
            clock_out=None if still_clocked_in else clock_in + timedelta(hours=8, minutes=-3 if i % 2 else 5),
            notes="Left early, approved by supervisor" if i % 4 == 0 else None,
        ))
    return await _insert_all(repo, "time-entries", records)


async def seed_payroll(client, employees: list[UUID]) -> list[UUID]:
    repo = SupabaseRepository(client, "employee_payroll_records", EmployeePayrollRecord, parent_field="employee_id")
    statuses = list(PayrollStatus)
    hours = [76.0, 76.0, 76.0, 48.0, 32.0, 20.0, 76.0, 76.0, 48.0, 60.0]
    rates = [32.50, 34.00, 42.75, 41.00, 29.50, 27.80, 38.20, 55.00, 34.00, 48.00]

    records = []
    for i in range(10):
        gross = round(hours[i] * rates[i], 2)
        deductions = round(gross * 0.19, 2)
        records.append(EmployeePayrollRecord(
            employee_id=employees[i],
            pay_period_start=_d(2026, 7, 6) + timedelta(days=(i % 4) * 14),
            pay_period_end=_d(2026, 7, 19) + timedelta(days=(i % 4) * 14),
            total_hours=hours[i], hourly_rate=rates[i], gross_pay=gross, deductions=deductions,
            net_pay=round(gross - deductions, 2), status=statuses[i % len(statuses)],
            notes="Includes overtime loading" if i % 3 == 0 else None,
        ))
    return await _insert_all(repo, "payroll", records)


async def main() -> None:
    await connect_to_supabase()
    client = get_supabase()
    try:
        print("Seeding top-level resources...")
        resident_ids = await seed_residents(client)
        employee_ids = await seed_employees(client)

        if not resident_ids or not employee_ids:
            print("Aborting: residents/employees must seed successfully before child resources.")
            return

        print("\nSeeding standalone resources...")
        await seed_complaints(client, resident_ids, employee_ids)
        await seed_appointments(client, employee_ids)

        print("\nSeeding resident-scoped resources...")
        await seed_medical_history(client, resident_ids)
        await seed_behaviour(client, resident_ids, employee_ids)
        await seed_medications(client, resident_ids)
        await seed_bowel_chart(client, resident_ids, employee_ids)
        await seed_sleep_chart(client, resident_ids, employee_ids)
        await seed_fall_risk(client, resident_ids, employee_ids)
        await seed_assistance(client, resident_ids, employee_ids)
        await seed_medical_inventory(client, resident_ids, employee_ids)
        await seed_incidents(client, resident_ids, employee_ids)

        print("\nSeeding employee-scoped resources...")
        await seed_supervision(client, employee_ids)
        await seed_registration(client, employee_ids)
        await seed_qualifications(client, employee_ids)
        await seed_performance(client, employee_ids)
        await seed_leave(client, employee_ids)
        await seed_contracts(client, employee_ids)
        await seed_availability(client, employee_ids)
        shift_ids = await seed_shifts(client, employee_ids)
        await seed_time_entries(client, employee_ids, shift_ids)
        await seed_payroll(client, employee_ids)

        print("\nDone.")
    finally:
        await close_supabase_connection()


if __name__ == "__main__":
    asyncio.run(main())
