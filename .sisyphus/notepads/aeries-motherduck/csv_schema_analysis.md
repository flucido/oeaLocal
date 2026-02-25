# AeRIES CSV Source Data Schema Analysis

**Analysis Date**: 2026-02-22  
**Source Path**: `/Users/flucido/Desktop/AeRIES test data/`  
**Years Covered**: 2020-2021 through 2025-2026 (6 academic years)  
**Total Domains**: 7

---

## Executive Summary

| Domain | Files | Total Rows | Avg Rows/Year | Columns | Key Fields |
|--------|-------|------------|---------------|---------|----------|
| **students** | 6 | 5,238 | 873 | 80 | StudentID, SchoolCode, Grade |
| **attendance_transformed** | 6 | 33,484 | 5,581 | 27 | StudentID, SchoolCode, DaysEnrolled |
| **grades_transformed** | 6 | 150,589 | 25,098 | 27 | StudentID, CourseID, MP_Mark |
| **discipline_transformed** | 6 | 7,309 | 1,218 | 57 | StudentID, IncidentID, ViolationCode1 |
| **enrollment** | 6 | 5,469 | 912 | 19 | StudentID, SchoolCode, EnterDate |
| **programs** | 6 | 13,538 | 2,256 | 10 | StudentID, ProgramCode |
| **gpa** | 6 | 5,238 | 873 | 27 | StudentID, GPA_CumulativeTotal |

**Total Records Across All Domains**: 220,865 records  
**Estimated Total Dataset Size**: ~100 MB (CSV), ~40 MB (Parquet with ZSTD)

---

## Domain 1: Students

### File Pattern
```
students/students_YYYY_YYYY.csv
```

### File Sizes
- 2020-2021: 381 KB (939 rows)
- 2021-2022: 358 KB (876 rows)
- 2022-2023: 351 KB (856 rows)
- 2023-2024: 350 KB (850 rows)
- 2024-2025: 357 KB (865 rows)
- 2025-2026: 353 KB (852 rows)

### Schema (80 columns)
```
StudentID, OldStudentID, CorrespondenceLanguageCode, CounselorNumber, 
StudentPersonalEmailAddress, NameSuffix, SchoolCode, StudentNumber, 
StateStudentID, LastName, FirstName, MiddleName, LastNameAlias, 
FirstNameAlias, MiddleNameAlias, Gender, Grade, GradeLevelShortDescription, 
GradeLevelLongDescription, Birthdate, ParentGuardianName, HomePhone, 
StudentMobilePhone, MailingAddress, MailingAddressCity, MailingAddressState, 
MailingAddressZipCode, MailingAddressZipExt, ResidenceAddress, 
ResidenceAddressCity, ResidenceAddressState, ResidenceAddressZipCode, 
ResidenceAddressZipExt, AddressVerified, EthnicityCode, RaceCode1, RaceCode2, 
RaceCode3, RaceCode4, RaceCode5, UserCode1-12, SchoolEnterDate, 
SchoolLeaveDate, DistrictEnterDate, Track, AttendanceProgramCodePrimary, 
AttendanceProgramCodeAdditional1-2, LockerNumber, LowSchedulingPeriod, 
HighSchedulingPeriod, InactiveStatusCode, FamilyKey, LanguageFluencyCode, 
HomeLanguageCode, ParentEdLevelCode, ParentEmailAddress, StudentEmailAddress, 
NetworkLoginID, EarlyWarningPoints, HomeRoomTeacherNumber, 
NotificationPreferenceCode, NextSchoolCode, NextGrade, 
NextGradeLevelShortDescription, NextGradeLevelLongDescription, 
RecordsReleaseCode, AcademicYear, ExtractedAt
```

### Key Fields for Parquet Optimization
- **Primary Key**: `StudentID` (string, unique)
- **Partitioning**: `AcademicYear` (string, format: "YYYY-YYYY")
- **Foreign Keys**: `SchoolCode` (string)
- **Dates**: `Birthdate`, `SchoolEnterDate`, `SchoolLeaveDate`, `DistrictEnterDate`, `ExtractedAt`
- **PII Fields** (requires hashing): `LastName`, `FirstName`, `MiddleName`, `ParentGuardianName`, `HomePhone`, `StudentMobilePhone`, `MailingAddress`, `ResidenceAddress`, `ParentEmailAddress`, `StudentEmailAddress`

### Data Types (inferred)
- IDs: string
- Names/Addresses: string
- Codes: string (categorical)
- Dates: date (YYYY-MM-DD format)
- Grade: integer
- ExtractedAt: timestamp

---

## Domain 2: Attendance (Transformed)

### File Pattern
```
attendance_transformed/attendance_YYYY_YYYY.csv
```

### File Sizes & Row Counts
- 2020-2021: 5,906 rows
- 2021-2022: 5,660 rows
- 2022-2023: 5,455 rows
- 2023-2024: 5,262 rows (834 rows/month avg)
- 2024-2025: 5,444 rows
- 2025-2026: 5,757 rows

### Schema (27 columns)
```
StudentID, AcademicYear, ExtractedAt, AttendanceProgramCodePrimary, 
ReportingSchoolCode, DaysCompleteIndependentStudy, 
DaysIncompleteIndependentStudy, DaysInSchoolSuspension, 
PeriodsExpectedToAttend, PeriodsAttended, PeriodsOutOfSchoolSuspension, 
PeriodsAttendedInSchoolSuspension, PeriodsExcusedAbsence, 
PeriodsUnexcusedAbsence, PeriodsCompleteIndependentStudy, 
PeriodsIncompleteIndependentStudy, SchoolYear, SchoolCode, DaysEnrolled, 
DaysPresent, DaysAbsence, DaysExcused, DaysUnexcused, DaysTardy, 
DaysOfTruancy, DaysSuspension
```

### Key Fields
- **Primary Key**: Composite (`StudentID` + `SchoolCode` + `AcademicYear`)
- **Partitioning**: `AcademicYear`
- **Foreign Keys**: `StudentID`, `SchoolCode`
- **Metrics**: All numeric columns (integers)
- **Dates**: `ExtractedAt` (timestamp)

### Data Types
- IDs/Codes: string
- Metrics: integer
- ExtractedAt: timestamp

---

## Domain 3: Grades (Transformed)

### File Pattern
```
grades_transformed/grades_YYYY_YYYY.csv
```

### File Sizes & Row Counts
- 2020-2021: 27,082 rows
- 2021-2022: 27,737 rows
- 2022-2023: 26,495 rows
- 2023-2024: 25,846 rows (largest dataset)
- 2024-2025: 28,776 rows
- 2025-2026: 14,653 rows (partial year)

**Total**: 150,589 grade records across 6 years

### Schema (27 columns)
```
StudentID, AcademicYear, ExtractedAt, SchoolCode, CourseID, CourseTitle, 
Period, SectionNumber, TeacherNumber, MP_PrimaryStaffID, MP_Hours, 
MP_AttendanceBasedGradesIndicator, MP_MarkingPeriod, MP_Mark, MP_Credit, 
MP_Comment1Code, MP_Comment2Code, MP_Comment3Code, MP_CitizenshipCode, 
MP_WorkHabitsCode, MP_TotalAbsences, MP_TotalTardies, MP_TotalDaysEnrolled, 
MP_TotalDaysPresent, MP_TotalExcusedAbsences, MP_TotalUnExcusedAbsences, 
MP_TotalDaysOfSuspension
```

### Key Fields
- **Primary Key**: Composite (`StudentID` + `CourseID` + `SectionNumber` + `MP_MarkingPeriod` + `AcademicYear`)
- **Partitioning**: `AcademicYear`
- **Foreign Keys**: `StudentID`, `SchoolCode`, `CourseID`, `TeacherNumber`
- **Grade Data**: `MP_Mark` (letter grade), `MP_Credit` (decimal)
- **Attendance Metrics**: All `MP_Total*` columns (integers)

### Data Types
- IDs: string
- MP_Mark: string (A, B, C, D, F, I, W, etc.)
- MP_Credit: decimal
- Counts/Hours: integer or decimal
- Boolean: boolean
- ExtractedAt: timestamp

---

## Domain 4: Discipline (Transformed)

### File Pattern
```
discipline_transformed/discipline_YYYY_YYYY.csv
```

### File Sizes & Row Counts
- 2020-2021: 168 KB (560 rows)
- 2021-2022: 254 KB (897 rows)
- 2022-2023: 519 KB (1,915 rows) - spike in incidents
- 2023-2024: 507 KB (1,803 rows)
- 2024-2025: 410 KB (1,376 rows)
- 2025-2026: 197 KB (758 rows)

**Total**: 7,309 discipline incidents

### Schema (57 columns)
```
StudentID, AcademicYear, ExtractedAt, ShortDescription, StaffReferral, 
ReferredByOther, SequenceNumber, IncidentDate, IncidentID, ExactTime, 
ApproximateTimeCode, SchoolOfIncidentCode, LocationCode, 
PossibleMotivationCode, WeaponTypeCode, Demerits, Initials, 
InstructionalSupportIndicator, Comment, IsSubstituteTeacherReferral, 
ViolationCode1-5, PreReferralInterventionCode1-3, UserCode1-8, 
Admin_StudentID, Admin_AssignedDays, Admin_AssignedHours, 
Admin_AssignedStartDate, Admin_AssignedEndDate, Admin_AssignedReturnDate, 
Admin_ReasonForDifferenceCode, Admin_DisciplinaryAssignmentSchoolCode, 
Admin_ActionDecisionDate, Admin_SequenceNumber, Admin_DispositionCode, 
Admin_Days, Admin_Hours, Admin_StartDate, Admin_EndDate, Admin_ReturnDate, 
Admin_ReturnStatusCode, Admin_ReturnLocationCode, Admin_ActionAuthorityCode, 
Admin_PlacementCode, Admin_ResultCode, Admin_SuspensionTagCode
```

### Key Fields
- **Primary Key**: `IncidentID` (string, unique per incident)
- **Composite Key**: (`StudentID` + `IncidentID` + `SequenceNumber`)
- **Partitioning**: `AcademicYear`
- **Foreign Keys**: `StudentID`, `SchoolOfIncidentCode`
- **Dates**: `IncidentDate`, `Admin_AssignedStartDate`, `Admin_AssignedEndDate`, `Admin_AssignedReturnDate`, `Admin_StartDate`, `Admin_EndDate`, `Admin_ReturnDate`, `ExtractedAt`
- **Key Analysis Fields**: `ViolationCode1-5`, `Admin_DispositionCode`, `Admin_Days`, `Admin_SuspensionTagCode`

### Data Types
- IDs: string
- Dates: date
- Codes: string (categorical)
- Days/Hours: integer
- Boolean flags: boolean
- Descriptions/Comments: string (free text)
- ExtractedAt: timestamp

---

## Domain 5: Enrollment

### File Pattern
```
enrollment/enrollment_YYYY_YYYY.csv
```

### File Sizes & Row Counts
- 2020-2021: 935 rows
- 2021-2022: 885 rows
- 2022-2023: 891 rows
- 2023-2024: 918 rows
- 2024-2025: 944 rows
- 2025-2026: 896 rows

**Total**: 5,469 enrollment records (likely 1 row per student-year)

### Schema (19 columns)
```
StudentID, InterIntraDistrictStateCode, NonpublicSchoolStateCode, 
NextSchoolCode, ReportingSchoolCode, SchoolCode, StudentNumber, AcademicYear, 
Track, AttendanceProgramCode, AttendanceProgramCodeAdditional1, 
AttendanceProgramCodeAdditional2, Grade, ElementaryTeacherNumber, 
ElementaryTeacherName, EnterDate, LeaveDate, ExitReasonCode, 
InterIntraDistrictTransferCode, ExtractedAt
```

### Key Fields
- **Primary Key**: Composite (`StudentID` + `SchoolCode` + `AcademicYear` + `EnterDate`)
- **Partitioning**: `AcademicYear`
- **Foreign Keys**: `StudentID`, `SchoolCode`, `NextSchoolCode`
- **Dates**: `EnterDate`, `LeaveDate`, `ExtractedAt`
- **Key Analysis Fields**: `Grade`, `ExitReasonCode`, `InterIntraDistrictTransferCode`

### Data Types
- IDs: string
- Codes: string
- Grade: integer
- Dates: date
- Teacher name: string
- ExtractedAt: timestamp

---

## Domain 6: Programs

### File Pattern
```
programs/programs_YYYY_YYYY.csv
```

### File Sizes & Row Counts
- 2020-2021: 264 KB (1,602 rows)
- 2021-2022: 293 KB (1,786 rows)
- 2022-2023: 310 KB (2,011 rows)
- 2023-2024: 349 KB (2,339 rows)
- 2024-2025: 424 KB (2,927 rows)
- 2025-2026: 420 KB (2,873 rows)

**Total**: 13,538 program participation records (growing trend)

### Schema (10 columns)
```
ExtendedProperties, StudentID, ProgramCode, ProgramDescription, 
EligibilityStartDate, EligibilityEndDate, ParticipationStartDate, 
ParticipationEndDate, AcademicYear, ExtractedAt
```

### Key Fields
- **Primary Key**: Composite (`StudentID` + `ProgramCode` + `ParticipationStartDate` + `AcademicYear`)
- **Partitioning**: `AcademicYear`
- **Foreign Keys**: `StudentID`
- **Dates**: `EligibilityStartDate`, `EligibilityEndDate`, `ParticipationStartDate`, `ParticipationEndDate`, `ExtractedAt`
- **Program Data**: `ProgramCode` (categorical), `ProgramDescription` (string)
- **Special**: `ExtendedProperties` (likely JSON or delimited string with additional metadata)

### Data Types
- StudentID: string
- Codes: string
- Descriptions: string
- Dates: date
- ExtendedProperties: string (may need JSON parsing)
- ExtractedAt: timestamp

---

## Domain 7: GPA (Grades GPA)

### File Pattern
```
grades_gpa/gpa_YYYY_YYYY.csv
```

### File Sizes & Row Counts
- 2020-2021: 138 KB (939 rows)
- 2021-2022: 130 KB (876 rows)
- 2022-2023: 128 KB (856 rows)
- 2023-2024: 126 KB (850 rows)
- 2024-2025: 129 KB (865 rows)
- 2025-2026: 126 KB (852 rows)

**Total**: 5,238 GPA records (matches students count - 1 per student-year)

### Schema (27 columns)
```
StudentID, SchoolCode, ClassRank, ClassSize, ClassRank1012, 
GPA_CumulativeAcademic, GPA_CumulativeTotal, GPA_CumulativeAcademic1012, 
GPA_CumulativeAcademicNonWeighted, GPA_CumulativeTotalNonWeighted, 
GPA_CumulativeAcademic1012NonWeighted, GradePointsCumulative, 
GPA_UC_Preliminary, GPA_CSU_Preliminary, GPA_CumulativeCitizenship, 
GPA_GradeReportingCitizenship, CreditsAttempted, CreditsCompleted, 
GPA_GradeReportingAcademic, GPA_GradeReportingTotal, 
GPA_GradeReportingAcademicNonWeighted, GPA_GradeReportingTotalNonWeighted, 
GradeReportingClassRank, GradeReportingClassSize, 
GradeReportingCreditsAttempted, GradeReportingCreditsCompleted, AcademicYear, 
ExtractedAt
```

### Key Fields
- **Primary Key**: Composite (`StudentID` + `SchoolCode` + `AcademicYear`)
- **Partitioning**: `AcademicYear`
- **Foreign Keys**: `StudentID`, `SchoolCode`
- **GPA Metrics**: All `GPA_*` columns (decimal, precision 2-4)
- **Class Rank**: `ClassRank`, `ClassSize`, `ClassRank1012` (integers)
- **Credits**: `CreditsAttempted`, `CreditsCompleted`, `GradeReportingCredits*` (decimal)

### Data Types
- IDs: string
- GPA values: decimal (scale 2-4)
- Ranks/Sizes: integer
- Credits: decimal
- ExtractedAt: timestamp

---

## Parquet Conversion Recommendations

### Partitioning Strategy
```
oss_framework/data/stage1/aeries/{domain}/year={academic_year}/*.parquet
```

Example:
```
stage1/aeries/students/year=2023-2024/part-000.parquet
stage1/aeries/attendance_transformed/year=2023-2024/part-000.parquet
```

### Compression Settings
```python
compression = 'ZSTD'
compression_level = 5
row_group_size = 256 * 1024 * 1024  # 256 MB
```

### Schema Validation
- Enforce NOT NULL on: `StudentID`, `AcademicYear`, `ExtractedAt`
- Validate date formats: `YYYY-MM-DD` for dates, `YYYY-MM-DD HH:MM:SS` for timestamps
- Validate grade levels: 1-12 (or K-12 with string encoding)
- Validate school codes: match reference table (if available)

### PII Handling
**Fields requiring SHA256 hashing** (from students domain):
- LastName, FirstName, MiddleName
- ParentGuardianName
- HomePhone, StudentMobilePhone
- MailingAddress, ResidenceAddress
- ParentEmailAddress, StudentEmailAddress
- NetworkLoginID

**Approach**: Store both `{field}` and `{field}_hash` in Stage1, then downstream dbt models use only `_hash` versions.

### Expected Output Sizes (Parquet with ZSTD level 5)
Based on CSV sizes and typical compression ratios:
- Students: ~60 KB/year → 360 KB total
- Attendance: ~150 KB/year → 900 KB total
- Grades: ~4 MB/year → 24 MB total
- Discipline: ~80 KB/year → 480 KB total
- Enrollment: ~40 KB/year → 240 KB total
- Programs: ~100 KB/year → 600 KB total
- GPA: ~30 KB/year → 180 KB total

**Total Parquet dataset size**: ~27 MB (vs. ~100 MB CSV) = 73% compression

---

## Pipeline Implementation Checklist

### CSV Reading
- [x] Verified all 7 domains have files for 6 years (2020-2026)
- [x] Identified column schemas for each domain
- [x] Confirmed file naming pattern: `{domain}_YYYY_YYYY.csv`
- [ ] Test pandas read_csv with sample files
- [ ] Handle potential encoding issues (UTF-8 vs Latin-1)
- [ ] Handle potential delimiter issues (comma vs tab)

### Parquet Writing
- [ ] Implement year-based partitioning
- [ ] Set ZSTD compression level 5
- [ ] Set row group size to 256 MB
- [ ] Add Parquet metadata (created_by, data_source, ingestion_timestamp)
- [ ] Validate output files are readable

### Data Quality
- [ ] Check for null StudentIDs
- [ ] Validate date formats
- [ ] Validate foreign key relationships (StudentID exists in students table)
- [ ] Check for duplicates within partitions
- [ ] Verify row counts match source CSVs

### Performance
- [ ] Measure ingestion time per domain
- [ ] Measure total ingestion time (target: < 5 minutes)
- [ ] Measure Parquet file sizes
- [ ] Test query performance on partitioned Parquet files

---

## Next Steps

1. **Create pipeline script**: `oss_framework/pipelines/aeries_to_parquet.py`
2. **Implement for students domain first** (simplest, 80 columns but predictable)
3. **Test with single year** (2023-2024)
4. **Extend to all years** for students
5. **Replicate pattern** for remaining 6 domains
6. **Run full ingestion** and validate output
7. **Update sync_raw_views script** to create DuckDB views over new Parquet files

---

## Notes & Gotchas

### Multi-Year Trends
- **Students**: Declining slightly (939 → 852)
- **Attendance**: Stable (~5,500/year)
- **Grades**: Stable (~26K/year, except 2025-2026 partial)
- **Discipline**: Spike in 2022-2023 (1,915 incidents) - post-COVID?
- **Enrollment**: Stable (~900/year)
- **Programs**: Growing (1,602 → 2,873) - increased program participation
- **GPA**: Matches students count exactly - confirms 1:1 relationship

### Data Quality Observations
- All domains have consistent column schemas across years
- ExtractedAt timestamp present in all domains
- AcademicYear format is consistent: "YYYY-YYYY"
- StudentID appears to be primary key across all domains (foreign key relationships)

### Potential Issues
1. **ExtendedProperties** in programs domain may need special parsing
2. **Discipline** has 57 columns with many optional fields (expect nulls)
3. **Students** has 80 columns including many PII fields requiring hashing
4. **Grades** 2025-2026 has half the rows (14,653 vs ~27K) - partial year data

---

**Analysis Complete**: Ready to implement aeries_to_parquet.py pipeline
