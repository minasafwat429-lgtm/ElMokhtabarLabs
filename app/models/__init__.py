from .user import User
from .patient_test import PatientTest 
from .test_catalog import TestCatalog
from .doctor import Doctor as OldDoctor

# Import new schema models
from .lab_schema import (
    Branch, Supplier, Patient, Doctor, Staff, Equipment, Sample, Test, Result, Payment,
    branch_equipment, equipment_tests, patient_tests, test_samples
)
