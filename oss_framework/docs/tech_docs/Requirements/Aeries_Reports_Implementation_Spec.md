# Aeries Reports Implementation Specification

## Executive Summary
This document provides comprehensive specifications for implementing Aeries reporting functionality across three major categories: Flex Scheduling Reports, Standard Scheduling Reports, and Student Data Reports. The implementation should support both traditional and flex scheduling environments.

## Step 1 Implementation Summary (October 2025)

This section records the concrete deliverables completed in Step 1:

- Environment Abstraction Layer
  - `SchedulingEnvironment` enum and `EnvironmentResolver` trait implemented with a default resolver.
  - `EnvAwareAttendanceRepository` added to route attendance queries by environment (Flex vs Traditional hook in place).

- Attendance Service Refactor
  - `AttendanceService` now depends on an `AttendanceRepository` abstraction.
  - `DefaultAttendanceService` alias wires `AeriesClient` + default resolver + env-aware repository.
  - Daily Attendance Summary aggregates present/absent/tardy by period; teacher/section breakdown structs added (population deferred).

- New API Endpoints (V2 Reports + Categories)
  - GET `/api/v5/reports/categories` — returns category groups and their report routes.
  - GET `/api/v5/reports/daily-attendance-summary?schoolCode&date`
  - GET `/api/v5/reports/d-and-f-report?schoolCode&markingPeriod`
  - GET `/api/v5/reports/honor-roll?schoolCode&term&gpaType&honorRollThreshold&highHonorRollThreshold`
  - GET `/api/v5/reports/chronic-absenteeism?minEnrollmentDays&chronicThresholdPct`
  - GET `/api/v5/reports/period-absence-summary?schoolCode&startDate&endDate`
  - Legacy bridge remains: `/api/v5/students/:student_id/reports/:report_type` (mock data for `attendance` and `grades`).

- Validation
  - Build: PASS; Tests: PASS; Static analysis: PASS; Security scan: PASS.

- Known Deferrals
  - Flex vs Traditional branching currently uses a unified endpoint; repository hook ready for CAT/FTF.
  - Teacher/section breakdown population pending schedule joins.
  - Additional categories (Student Information, Scheduling & Class Management, Medical & Health) have placeholders.

## Table of Contents
1. [Report Categories Overview](#report-categories-overview)
2. [Attendance Reports](#attendance-reports)
3. [Student Data Reports](#student-data-reports)
4. [Grade Reporting & Gradebook](#grade-reporting--gradebook)
5. [Scheduling Reports](#scheduling-reports)
6. [Medical Reports](#medical-reports)
7. [Implementation Architecture](#implementation-architecture)
8. [Data Requirements](#data-requirements)
9. [UI/UX Recommendations](#uiux-recommendations)
10. [Priority Implementation Plan](#priority-implementation-plan)

---

## Report Categories Overview

### 1. Primary Report Categories
The system should support three main report categories:

- **Attendance & Enrollment Reports**
- **Academic & Grade Reports**
- **Student Information Reports**
- **Scheduling & Class Management Reports**
- **Medical & Health Reports**

### 2. Environment Support

Reports must function in:

- Traditional scheduling environments
- Flex scheduling environments
- Elementary with Master Schedule
- Secondary scheduling systems

---

## Attendance Reports

### Core Attendance Reports (Must Have)

These reports are essential for daily operations and compliance:

#### 1. Daily Attendance Summary

- **Purpose**: Provides daily snapshot of attendance across the school
- **Data Elements**:
  - Student counts by period/time
  - Absence totals by type
  - Tardy statistics
  - Teacher/section breakdowns
- **Flex Support**: Uses CAT table instead of ATT for flex schools

#### 2. Missing Attendance Report

- **Purpose**: Identifies classes/periods missing attendance data
- **Key Features**:
  - Real-time identification of unsubmitted attendance
  - Teacher/period matrix view
  - Support for flex periods (FTF.STI)
- **Priority**: Critical for daily operations

#### 3. Class Period Absence Summary

- **Purpose**: Summarizes absences by class period
- **Data Elements**:
  - Primary teacher identification (SSE table)
  - Flex period support
  - Calendar day analysis (CCD table)
  - Semester totals

#### 4. Attendance Calendar Report

- **Purpose**: Visual calendar view of attendance patterns
- **Features**:
  - Bell schedule integration (BSD table)
  - Custom schedule indicators
  - Legend for special day types

### Additional Attendance Reports

#### 5. Perfect Attendance Tracking

- Students with perfect attendance
- Period-specific perfect attendance
- Date range flexibility

#### 6. Consecutive Absence Monitoring

- Students with N+ consecutive absences
- Alert generation capability
- Parent notification integration

#### 7. Attendance Letters & Notifications

- District attendance letters
- Absence verification letters
- Parent notification workflows

---

## Student Data Reports

### Essential Student Information Reports

#### 1. Student Demographic Reports

- **Student Data Printout**
  - Demographics
  - Enrollment information
  - Student photo
  - Schedule option
- **Student Directory**
  - Sort by grade/name/counselor/address
  - Contact information
  - Family groupings

#### 2. Emergency & Safety Reports

- **Emergency Student Listing**
  - Health problems
  - Emergency contacts
  - Red flag indicators (CON.RF)
  - Primary class tracking for elementary
- **Emergency Cards**
  - Contact information
  - Medical alerts
  - Special instructions

#### 3. Student Enrollment Reports

- **Active Students by School and Grade**
  - Matrix view by school/grade
  - Real-time enrollment counts
- **Student Distribution Reports**
  - Bar graphs by grade level
  - Special program inclusion
  - Ethnic distribution analysis

### Special Program Reports

#### 1. English Learner Reports

- **Class Percentage Reports**
  - EL percentage by class
  - Teacher/section breakdown
- **Language Assessment Data**
  - Assessment history
  - Progress tracking

#### 2. Special Education Reports

- **Class Lists with SPED Info**
- **Student Disability Graphs**
- **IEP tracking integration**

---

## Grade Reporting & Gradebook

### Core Grade Reports

#### 1. Grade Report Cards

- **Features**:
  - Multiple marking periods
  - Standards-based options
  - Comments integration
  - Flex period support

#### 2. Grade Analysis Reports

- **Mark Analysis Report**
  - Teacher grade distribution
  - Course/section statistics
  - Primary teacher filtering
- **Mark Verification Listing**
  - Immediate post-submission verification
  - Teacher review process
  - Correction tracking

#### 3. Missing Mark Reports

- **Purpose**: Identify incomplete grading
- **Features**:
  - Teacher/class grouping
  - Student listing with gaps
  - Deadline tracking

#### 4. Grade History Tracking

- Historical grade records
- Transcript preparation
- Credit accumulation

---

## Scheduling Reports

### Master Schedule Reports

#### 1. Master Schedule Overview

- **Core Elements**:
  - Section listings with enrollment
  - Teacher assignments (primary teacher support)
  - Room allocations
  - Period/flex time mapping

#### 2. Master Schedule Board

- **Visual Matrix Display**:
  - Teacher x Period grid
  - Section information per cell
  - Room conflicts identification
  - Class load visualization

#### 3. Room Availability Report

- **Features**:
  - Room x Period matrix
  - Availability indicators:
    - Available (blank)
    - Class scheduled (X)
    - Overlapping periods (O)
  - Date-specific views

### Student Scheduling Reports

#### 1. Student Schedule Listings

- **Multiple Formats**:
  - Traditional period view
  - Flex time view
  - Wide format option
- **Locator Cards**:
  - Multiple format options
  - Distribution-ready layouts
  - Emergency contact integration

#### 2. Schedule Analysis Reports

- **Incomplete Schedules**
  - Gap identification
  - Period range analysis
- **Double Period Detection**
  - Conflict identification
  - Section overlap analysis
- **Load Balancing**
  - Students with >N or <N periods
  - Academic weight distribution

### Course Request Management

#### 1. Course Request Reports

- **Request Analysis**
  - Total requests by course
  - Grade level breakdowns
  - Conflict matrix
- **Parent Communications**
  - Request verification letters
  - Schedule confirmation

#### 2. Scheduling Process Reports

- **Reject Analysis**
  - Student rejection reasons
  - Course conflict tracking
  - Counselor assignments
- **Class Load Analysis**
  - Section capacity
  - Average class sizes
  - Gender/grade distributions

---

## Medical Reports

### Health Screening Reports

#### 1. Immunization Management

- **Immunization Status Reports**
  - Compliance tracking
  - Missing immunizations
  - Age/grade requirements
- **Immunization Cards**
  - State-specific formats
  - Blue card support (CA)

#### 2. Health Screening Records

- **Vision Screening**
- **Hearing Screening**
- **Dental Records**
- **Scoliosis Screening**
- **Physical Information**

#### 3. Medical Management

- **Medication Tracking**
  - Current medications
  - Dose history
  - Administration logs
- **Medical History**
  - Chronic conditions
  - Allergy tracking
  - Emergency procedures

---

## Implementation Architecture

### Technical Requirements

#### 1. Database Integration

**Key Tables for Flex Scheduling**:
- `SSE/SSM`: Section Staff Members
- `FTF`: Flex Time Framework
- `CCL`: Class Calendar
- `CAT`: Course Attendance (flex)
- `ATT`: Traditional Attendance
- `CCD`: Calendar Class Days
- `BSD`: Bell Schedule Days

#### 2. Report Generation Engine

```rust
// Suggested Rust implementation structure
pub struct ReportEngine {
    pub report_type: ReportType,
    pub scheduling_mode: SchedulingMode,
    pub data_source: DataSource,
    pub output_format: OutputFormat,
}

pub enum SchedulingMode {
    Traditional,
    Flex,
    Elementary,
    Secondary,
}

pub enum OutputFormat {
    PDF,
    Excel,
    CSV,
    HTML,
    Print,
}
```

#### 3. Data Processing Pipeline

1. **Data Extraction**
   - Query optimization for large datasets
   - Caching frequently used data
   - Real-time vs. batch processing

2. **Data Transformation**
   - Flex period mapping
   - Primary teacher resolution
   - Calendar day calculations

3. **Report Rendering**
   - Template-based generation
   - Dynamic formatting
   - Multi-format export

### API Design

#### REST API Endpoints

```text
/api/reports/
  /attendance/
    /daily-summary
    /missing-attendance
    /period-absences
    /calendar
  /students/
    /demographics
    /emergency-cards
    /enrollment
  /grades/
    /report-cards
    /analysis
    /verification
  /scheduling/
    /master-schedule
    /room-availability
    /student-schedules
  /medical/
    /immunizations
    /screenings
    /medications
```

---

## Data Requirements

### Core Data Elements

#### 1. Student Information

- Demographics (STU table)
- Enrollment history (ENR)
- Contact information (CON)
- Program participation (PGM)

#### 2. Attendance Data

- Traditional attendance (ATT)
- Course attendance (CAR/CAT)
- Absence codes and types
- Bell schedules (BSD)

#### 3. Academic Data

- Grades and marks
- Course enrollments (SEC)
- Teacher assignments (SSE/SSM)
- Credit accumulation

#### 4. Scheduling Data

- Master schedule (MST)
- Scheduling master (SMS)
- Flex periods (FTF)
- Class calendars (CCL)

### Data Validation Requirements

#### 1. Integrity Checks

- Duplicate enrollment detection
- Schedule conflict validation
- Grade submission verification
- Attendance completion monitoring

#### 2. Compliance Validation

- Immunization requirements
- Attendance thresholds
- Grade reporting deadlines
- Special education mandates

---

## UI/UX Recommendations

### Report Selection Interface

#### 1. Category-Based Navigation

```text
Reports Dashboard
├── Quick Access (Frequently Used)
├── Attendance & Enrollment
├── Student Information
├── Academic & Grades
├── Scheduling
├── Medical & Health
└── Custom Reports
```

#### 2. Search and Filter Options

- Text search across report names
- Filter by:
  - Report category
  - User role permissions
  - Scheduling type (traditional/flex)
  - School level (elementary/secondary)

### Report Configuration

#### 1. Common Parameters

- Date range selection
- Student/class selection
- Output format choice
- Delivery method (view/email/print)

#### 2. Advanced Options

- Custom field selection
- Sort order preferences
- Grouping options
- Summary level choices

### Report Output Features

#### 1. Interactive Elements

- Drill-down capabilities
- Export options
- Print preview
- Email distribution

#### 2. Visualization Options

- Charts and graphs where appropriate
- Color coding for categories
- Visual indicators for alerts
- Progress bars for completion status

---

## Priority Implementation Plan

### Phase 1: Core Operations (Weeks 1-4)

High Priority - Daily Use Reports

1. **Attendance Module**
   - Daily Attendance Summary
   - Missing Attendance Report
   - Class Period Absences
   - Attendance Calendar

2. **Student Information Module**
   - Emergency Student Listing
   - Student Demographics
   - Contact Information Reports

3. **Basic Scheduling**
   - Master Schedule Display
   - Room Availability
   - Student Schedule Listing

### Phase 2: Academic Management (Weeks 5-8)

Medium Priority - Periodic Use

1. **Grade Reporting**
   - Report Cards
   - Grade Analysis
   - Missing Marks
   - Verification Reports

2. **Course Management**
   - Course Request Reports
   - Scheduling Analysis
   - Class Load Reports

3. **Student Tracking**
   - Perfect Attendance
   - Consecutive Absences
   - Program Participation

### Phase 3: Comprehensive Features (Weeks 9-12)

Lower Priority - Specialized Use

1. **Medical Module**
   - Immunization Reports
   - Health Screenings
   - Medication Management

2. **Advanced Analytics**
   - Distribution Reports
   - Trend Analysis
   - Comparative Reports

3. **Communication Tools**
   - Parent Letters
   - Notification Systems
   - Bulk Communications

### Phase 4: Enhancement & Optimization (Weeks 13-16)

Optimization & Polish

1. **Performance Tuning**
   - Query optimization
   - Caching implementation
   - Batch processing

2. **User Experience**
   - Custom report builder
   - Saved report configurations
   - Scheduled report delivery

3. **Integration Features**
   - External system exports
   - API enhancements
   - Mobile accessibility

---

## Testing Requirements

### 1. Unit Testing

- Individual report generation
- Data transformation logic
- Flex vs. traditional handling

### 2. Integration Testing

- Database connectivity
- Multi-table joins
- Performance under load

### 3. User Acceptance Testing

- Report accuracy verification
- Format compliance
- Usability assessment

### 4. Performance Benchmarks

- Report generation: < 5 seconds for standard reports
- Batch processing: 100 students/second
- Concurrent users: Support 50+ simultaneous report requests

---

## Compliance & Security

### 1. Data Privacy

- FERPA compliance
- Role-based access control
- Audit logging for report access

### 2. Data Retention

- Historical report archiving
- Purge policies
- Backup procedures

### 3. Security Features

- Encrypted data transmission
- Secure report storage
- User authentication
- Session management

---

## Maintenance & Support

### 1. Documentation Requirements

- User guides per report
- Administrator documentation
- API documentation
- Troubleshooting guides

### 2. Training Materials

- Video tutorials
- Quick reference cards
- Best practices guide
- FAQ documentation

### 3. Support Structure

- Tiered support model
- Issue tracking system
- Feature request process
- Regular update schedule

---

## Appendices

### A. Report Template Examples

[Detailed templates for each report type would be included here]

### B. Database Schema References

[Complete table and field definitions]

### C. Sample Report Outputs

[Visual examples of each report format]

### D. Error Handling Guidelines

[Common errors and resolution procedures]

### E. Performance Optimization Tips

[Best practices for report efficiency]

---

## Version History

- v1.0 - Initial specification document
- Date: October 2025
- Author: System Architect Team

## Next Steps

1. Review and approve specification
2. Assign development teams
3. Create detailed technical designs
4. Begin Phase 1 implementation
5. Establish testing protocols
6. Plan user training sessions
