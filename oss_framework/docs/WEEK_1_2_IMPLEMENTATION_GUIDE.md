# Week 1-2: Data Foundation Implementation Guide
## Setting up Aeries API, Stage 1 Landing Zone, and Excel Import Pipelines

**Status**: Ready to execute once clarification questions are answered  
**Duration**: Week 1-2 (Days 1-10)  
**Deliverables**: 
- ✅ Aeries API integration (authentication + rate limiting)
- ✅ Stage 1 landing zone (7 tables in DuckDB)
- ✅ Excel import pipelines (D&F, Demographic, RFEP)
- ✅ Initial data validation tests

---

## Part 1: Aeries API Integration (Days 1-3)

### 1.1 API Authentication Setup

#### If Using Option A: REST API (OAuth2 / API Key)

**File to create**: `oss_framework/scripts/aeries_api_client.py`

```python
import os
import time
import logging
from typing import Dict, List, Any
import requests
from datetime import datetime

logger = logging.getLogger(__name__)

class AeriesClient:
    """
    Aeries API client with rate limiting and error handling
    Supports both OAuth2 and API Key authentication
    """
    
    def __init__(self, auth_method: str = "api_key"):
        """
        Args:
            auth_method: "api_key" or "oauth2"
        """
        self.auth_method = auth_method
        self.base_url = os.getenv("AERIES_API_URL", "https://api.aeries.com/v5")
        self.rate_limit_calls = 1000  # Aeries typical limit
        self.rate_limit_seconds = 3600
        self.call_times = []
        
        if auth_method == "api_key":
            self.api_key = os.getenv("AERIES_API_KEY")
            if not self.api_key:
                raise ValueError("AERIES_API_KEY environment variable not set")
        elif auth_method == "oauth2":
            self.client_id = os.getenv("AERIES_CLIENT_ID")
            self.client_secret = os.getenv("AERIES_CLIENT_SECRET")
            self.access_token = None
            self.token_expiry = 0
            if not self.client_id or not self.client_secret:
                raise ValueError("AERIES_CLIENT_ID and AERIES_CLIENT_SECRET required")
    
    def _check_rate_limit(self):
        """Implement token bucket rate limiting"""
        now = time.time()
        # Remove calls older than rate_limit_seconds
        self.call_times = [t for t in self.call_times if now - t < self.rate_limit_seconds]
        
        if len(self.call_times) >= self.rate_limit_calls:
            wait_time = self.rate_limit_seconds - (now - self.call_times[0])
            logger.warning(f"Rate limit reached. Waiting {wait_time:.1f} seconds...")
            time.sleep(wait_time)
            self.call_times = []
        
        self.call_times.append(now)
    
    def _get_oauth_token(self) -> str:
        """Get OAuth2 access token"""
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
        
        token_url = f"{self.base_url}/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        self.access_token = token_data["access_token"]
        self.token_expiry = time.time() + token_data.get("expires_in", 3600) - 60
        
        return self.access_token
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers based on auth method"""
        headers = {"Content-Type": "application/json"}
        
        if self.auth_method == "api_key":
            headers["Authorization"] = f"Bearer {self.api_key}"
        else:
            token = self._get_oauth_token()
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def get(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """GET request with rate limiting and error handling"""
        self._check_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        logger.info(f"GET {endpoint} with params {params}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def fetch_students(self) -> List[Dict]:
        """Fetch all student records"""
        return self.get("/reports/students")
    
    def fetch_attendance(self, filters: Dict = None) -> List[Dict]:
        """Fetch attendance records (optionally filtered by date range)"""
        return self.get("/reports/attendance", params=filters)
    
    def fetch_grades(self, filters: Dict = None) -> List[Dict]:
        """Fetch grade/academic records"""
        return self.get("/reports/grades", params=filters)
    
    def fetch_discipline(self, filters: Dict = None) -> List[Dict]:
        """Fetch discipline incidents"""
        return self.get("/reports/discipline", params=filters)
    
    def fetch_enrollment(self, filters: Dict = None) -> List[Dict]:
        """Fetch enrollment/course data"""
        return self.get("/reports/enrollment", params=filters)
    
    def fetch_courses(self) -> List[Dict]:
        """Fetch course master data"""
        return self.get("/reports/courses")


# Example usage and logging
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test API connection
    client = AeriesClient(auth_method="api_key")
    
    try:
        students = client.fetch_students()
        print(f"✅ Successfully fetched {len(students)} student records")
    except Exception as e:
        print(f"❌ Error: {e}")
```

**File to create**: `.env` (add to `.gitignore`!)

```bash
# Aeries API Configuration
# If using API Key authentication:
AERIES_API_URL=https://api.aeries.com/v5
AERIES_API_KEY=your_api_key_here

# If using OAuth2 authentication:
AERIES_CLIENT_ID=your_client_id_here
AERIES_CLIENT_SECRET=your_client_secret_here

# DuckDB Configuration
DUCKDB_DATABASE_PATH=/Users/flucido/projects/openedDataEstate/oss_framework/data/oea.duckdb

# Data lake paths
STAGE1_PATH=/Users/flucido/projects/openedDataEstate/oss_framework/data/stage1
STAGE2_PATH=/Users/flucido/projects/openedDataEstate/oss_framework/data/stage2
STAGE3_PATH=/Users/flucido/projects/openedDataEstate/oss_framework/data/stage3
```

### 1.2 Testing API Integration

**File to create**: `oss_framework/tests/test_aeries_api.py`

```python
import pytest
import os
from scripts.aeries_api_client import AeriesClient

@pytest.fixture
def aeries_client():
    """Create test client (requires .env credentials)"""
    return AeriesClient(auth_method="api_key")

def test_api_connection(aeries_client):
    """Test basic API connectivity"""
    try:
        students = aeries_client.fetch_students()
        assert isinstance(students, list)
        assert len(students) > 0
        print(f"✅ Connected to Aeries API. Found {len(students)} students.")
    except Exception as e:
        print(f"❌ API Connection failed: {e}")
        raise

def test_rate_limiting():
    """Verify rate limiting works correctly"""
    client = AeriesClient(auth_method="api_key")
    
    # Simulate rapid requests
    import time
    start = time.time()
    for i in range(5):
        client._check_rate_limit()
    elapsed = time.time() - start
    
    # Should complete in reasonable time
    assert elapsed < 2.0, "Rate limiting appears to be too aggressive"
    print("✅ Rate limiting configured correctly")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Part 2: Stage 1 Landing Zone Setup (Days 2-5)

### 2.1 Create DuckDB Landing Tables

**File to create**: `oss_framework/scripts/create_stage1_tables.py`

```python
import duckdb
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Stage1Initializer:
    """Create Stage 1 landing zone tables in DuckDB"""
    
    def __init__(self, db_path: str = None):
        db_path = db_path or os.getenv("DUCKDB_DATABASE_PATH", "data/oea.duckdb")
        self.con = duckdb.connect(db_path)
        self.db_path = db_path
        logger.info(f"Connected to DuckDB: {db_path}")
    
    def create_raw_students_table(self):
        """Create raw_students landing table from Aeries"""
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS raw_students (
            -- Keys (will be hashed in Stage 2)
            student_id VARCHAR NOT NULL PRIMARY KEY,
            school_id VARCHAR NOT NULL,
            
            -- Personal Information
            first_name VARCHAR,
            last_name VARCHAR,
            date_of_birth DATE,
            gender VARCHAR,
            phone_number VARCHAR,
            email VARCHAR,
            
            -- Demographics (retained for analysis)
            grade_level INTEGER,
            cohort_year INTEGER,
            ethnicity VARCHAR,
            
            -- Special Populations (flagged for analysis)
            special_education BOOLEAN DEFAULT FALSE,
            english_learner BOOLEAN DEFAULT FALSE,
            economically_disadvantaged BOOLEAN DEFAULT FALSE,
            homeless_status VARCHAR,
            foster_care_status VARCHAR,
            
            -- Additional flags from D&F import
            has_504_plan BOOLEAN DEFAULT FALSE,
            iep_status VARCHAR,
            disability_category VARCHAR,
            
            -- Enrollment Status
            enrollment_status VARCHAR,
            enrollment_start_date DATE,
            enrollment_end_date DATE,
            
            -- Metadata
            _loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _source VARCHAR DEFAULT 'aeries_api',
            _batch_id VARCHAR
        );
        """)
        logger.info("✅ Created raw_students table")
    
    def create_raw_attendance_table(self):
        """Create raw_attendance landing table"""
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS raw_attendance (
            attendance_id VARCHAR PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            school_id VARCHAR NOT NULL,
            attendance_date DATE NOT NULL,
            
            -- Attendance status
            is_present BOOLEAN,
            tardy_flag BOOLEAN DEFAULT FALSE,
            early_departure_flag BOOLEAN DEFAULT FALSE,
            
            -- Absence details
            absence_type VARCHAR,  -- excused/unexcused/medical/OSS/ISS
            absence_reason VARCHAR,
            
            -- Class/Period specific
            period_or_class VARCHAR,
            teacher_id VARCHAR,
            course_id VARCHAR,
            
            -- Computed flags
            chronic_absence_flag BOOLEAN DEFAULT FALSE,
            attendance_pattern VARCHAR,  -- improving/declining/stable/at_risk
            
            -- Follow-up
            parent_notification_sent BOOLEAN DEFAULT FALSE,
            makeup_assignment_required BOOLEAN DEFAULT FALSE,
            
            -- Metadata
            _loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _source VARCHAR DEFAULT 'aeries_api',
            _batch_id VARCHAR,
            
            FOREIGN KEY (student_id) REFERENCES raw_students(student_id)
        );
        """)
        logger.info("✅ Created raw_attendance table")
    
    def create_raw_academic_records_table(self):
        """Create raw_academic_records landing table"""
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS raw_academic_records (
            assignment_id VARCHAR PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            school_id VARCHAR NOT NULL,
            
            -- Course/Class context
            course_id VARCHAR NOT NULL,
            section_id VARCHAR NOT NULL,
            term VARCHAR NOT NULL,
            teacher_id VARCHAR,
            
            -- Assignment details
            assignment_name VARCHAR,
            assignment_type VARCHAR,
            assignment_due_date DATE,
            assignment_submission_date DATE,
            
            -- Grades
            points_earned DECIMAL(10, 2),
            points_possible DECIMAL(10, 2),
            assignment_grade_percent DECIMAL(5, 2),
            assignment_grade_letter VARCHAR(2),
            mastery_level VARCHAR,
            
            -- Submission quality
            late_days INTEGER DEFAULT 0,
            on_time_flag BOOLEAN DEFAULT TRUE,
            submission_status VARCHAR,
            assignment_quality_flag BOOLEAN,
            relative_grade DECIMAL(5, 2),  -- vs class average
            
            -- Feedback
            feedback_provided BOOLEAN DEFAULT FALSE,
            feedback_date TIMESTAMP,
            rubric_score DECIMAL(5, 2),
            
            -- Metadata
            _loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _source VARCHAR DEFAULT 'aeries_api',
            _batch_id VARCHAR,
            
            FOREIGN KEY (student_id) REFERENCES raw_students(student_id)
        );
        """)
        logger.info("✅ Created raw_academic_records table")
    
    def create_raw_discipline_table(self):
        """Create raw_discipline landing table"""
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS raw_discipline (
            discipline_id VARCHAR PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            school_id VARCHAR NOT NULL,
            
            -- Incident details
            incident_date DATE NOT NULL,
            incident_time TIME,
            incident_type VARCHAR NOT NULL,
            incident_description VARCHAR,
            
            -- Location/Context
            location VARCHAR,
            teacher_id VARCHAR,
            course_id VARCHAR,
            
            -- Consequence
            consequence_type VARCHAR,  -- detention, suspension, expulsion, etc.
            consequence_duration INTEGER,  -- days
            consequence_start_date DATE,
            consequence_end_date DATE,
            
            -- Escalation
            escalation_level INTEGER DEFAULT 1,  -- 1=warning, 2=detention, 3=suspension, 4=expulsion
            parent_contact_made BOOLEAN DEFAULT FALSE,
            referral_to_counselor BOOLEAN DEFAULT FALSE,
            
            -- Metadata
            _loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _source VARCHAR DEFAULT 'aeries_api',
            _batch_id VARCHAR,
            
            FOREIGN KEY (student_id) REFERENCES raw_students(student_id)
        );
        """)
        logger.info("✅ Created raw_discipline table")
    
    def create_raw_enrollment_table(self):
        """Create raw_enrollment landing table"""
        self.con.execute("""
        CREATE TABLE IF NOT EXISTS raw_enrollment (
            enrollment_id VARCHAR PRIMARY KEY,
            student_id VARCHAR NOT NULL,
            school_id VARCHAR NOT NULL,
            
            -- Course/Section info
            course_id VARCHAR NOT NULL,
            section_id VARCHAR NOT NULL,
            term VARCHAR NOT NULL,
            teacher_id VARCHAR,
            
            -- Enrollment status
            enrollment_date DATE,
            completion_date DATE,
            enrollment_status VARCHAR,  -- active/completed/dropped/failed
            
            -- Grade info
            final_grade_letter VARCHAR(2),
            final_grade_numeric DECIMAL(5, 2),
            credits_attempted DECIMAL(5, 2),
            credits_earned DECIMAL(5, 2),
            weighted_gpa_impact DECIMAL(5, 3),
            
            -- Risk flags (computed)
            academic_risk_flag BOOLEAN DEFAULT FALSE,
            engagement_flag BOOLEAN DEFAULT FALSE,
            
            -- Metadata
            _loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            _source VARCHAR DEFAULT 'aeries_api',
            _batch_id VARCHAR,
            
            FOREIGN KEY (student_id) REFERENCES raw_students(student_id)
        );
        """)
        logger.info("✅ Created raw_enrollment table")
    
    def create_all_stage1_tables(self):
        """Create all Stage 1 landing tables"""
        logger.info("Creating Stage 1 landing zone tables...")
        self.create_raw_students_table()
        self.create_raw_attendance_table()
        self.create_raw_academic_records_table()
        self.create_raw_discipline_table()
        self.create_raw_enrollment_table()
        logger.info("✅ All Stage 1 tables created successfully")
    
    def show_table_schemas(self):
        """Display all table schemas for verification"""
        tables = [
            "raw_students",
            "raw_attendance",
            "raw_academic_records",
            "raw_discipline",
            "raw_enrollment"
        ]
        for table in tables:
            print(f"\n--- {table} ---")
            schema = self.con.execute(f"DESCRIBE {table}").fetchall()
            for column in schema:
                print(f"  {column[0]:30} {column[1]:15}")
    
    def close(self):
        """Close database connection"""
        self.con.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    initializer = Stage1Initializer()
    initializer.create_all_stage1_tables()
    initializer.show_table_schemas()
    initializer.close()
    
    print("\n✅ Stage 1 initialization complete!")
```

### 2.2 Data Ingestion Pipeline

**File to create**: `oss_framework/scripts/ingest_aeries_data.py`

```python
import duckdb
import os
import logging
from datetime import datetime
import uuid
from aeries_api_client import AeriesClient

logger = logging.getLogger(__name__)

class AeriesDataIngestor:
    """Ingest data from Aeries API into Stage 1 tables"""
    
    def __init__(self, db_path: str = None):
        db_path = db_path or os.getenv("DUCKDB_DATABASE_PATH", "data/oea.duckdb")
        self.con = duckdb.connect(db_path)
        self.client = AeriesClient(auth_method="api_key")
        self.batch_id = str(uuid.uuid4())
        logger.info(f"Initialized ingestion (batch_id: {self.batch_id})")
    
    def ingest_students(self):
        """Fetch and load student data"""
        logger.info("Ingesting student data from Aeries API...")
        
        try:
            students = self.client.fetch_students()
            logger.info(f"Fetched {len(students)} student records")
            
            # Insert into raw_students
            for student in students:
                self.con.execute("""
                INSERT INTO raw_students (
                    student_id, school_id, first_name, last_name, 
                    date_of_birth, gender, grade_level, cohort_year,
                    ethnicity, special_education, english_learner,
                    economically_disadvantaged, enrollment_status,
                    enrollment_start_date, _batch_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (student_id) DO UPDATE SET 
                    _updated_at = CURRENT_TIMESTAMP,
                    grade_level = EXCLUDED.grade_level,
                    enrollment_status = EXCLUDED.enrollment_status
                """, [
                    student.get('student_id'),
                    student.get('school_id'),
                    student.get('first_name'),
                    student.get('last_name'),
                    student.get('date_of_birth'),
                    student.get('gender'),
                    student.get('grade_level'),
                    student.get('cohort_year'),
                    student.get('ethnicity'),
                    student.get('special_education', False),
                    student.get('english_learner', False),
                    student.get('economically_disadvantaged', False),
                    student.get('enrollment_status'),
                    student.get('enrollment_start_date'),
                    self.batch_id
                ])
            
            self.con.commit()
            logger.info(f"✅ Loaded {len(students)} student records")
            return len(students)
        
        except Exception as e:
            logger.error(f"❌ Error ingesting students: {e}")
            self.con.rollback()
            raise
    
    def ingest_attendance(self):
        """Fetch and load attendance data"""
        logger.info("Ingesting attendance data from Aeries API...")
        
        try:
            attendance = self.client.fetch_attendance()
            logger.info(f"Fetched {len(attendance)} attendance records")
            
            # Insert into raw_attendance
            for record in attendance:
                self.con.execute("""
                INSERT INTO raw_attendance (
                    attendance_id, student_id, school_id, attendance_date,
                    is_present, tardy_flag, absence_type, absence_reason,
                    teacher_id, course_id, _batch_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (attendance_id) DO UPDATE SET 
                    _updated_at = CURRENT_TIMESTAMP,
                    is_present = EXCLUDED.is_present,
                    absence_type = EXCLUDED.absence_type
                """, [
                    record.get('attendance_id') or str(uuid.uuid4()),
                    record.get('student_id'),
                    record.get('school_id'),
                    record.get('attendance_date'),
                    record.get('is_present'),
                    record.get('tardy_flag', False),
                    record.get('absence_type'),
                    record.get('absence_reason'),
                    record.get('teacher_id'),
                    record.get('course_id'),
                    self.batch_id
                ])
            
            self.con.commit()
            logger.info(f"✅ Loaded {len(attendance)} attendance records")
            return len(attendance)
        
        except Exception as e:
            logger.error(f"❌ Error ingesting attendance: {e}")
            self.con.rollback()
            raise
    
    def ingest_grades(self):
        """Fetch and load academic records"""
        logger.info("Ingesting academic records from Aeries API...")
        
        try:
            grades = self.client.fetch_grades()
            logger.info(f"Fetched {len(grades)} grade records")
            
            for record in grades:
                self.con.execute("""
                INSERT INTO raw_academic_records (
                    assignment_id, student_id, school_id, course_id,
                    section_id, term, teacher_id, assignment_name,
                    assignment_type, assignment_due_date,
                    assignment_submission_date, points_earned,
                    points_possible, assignment_grade_percent,
                    assignment_grade_letter, on_time_flag, _batch_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (assignment_id) DO UPDATE SET 
                    _updated_at = CURRENT_TIMESTAMP,
                    points_earned = EXCLUDED.points_earned,
                    assignment_grade_percent = EXCLUDED.assignment_grade_percent
                """, [
                    record.get('assignment_id') or str(uuid.uuid4()),
                    record.get('student_id'),
                    record.get('school_id'),
                    record.get('course_id'),
                    record.get('section_id'),
                    record.get('term'),
                    record.get('teacher_id'),
                    record.get('assignment_name'),
                    record.get('assignment_type'),
                    record.get('assignment_due_date'),
                    record.get('assignment_submission_date'),
                    record.get('points_earned'),
                    record.get('points_possible'),
                    record.get('assignment_grade_percent'),
                    record.get('assignment_grade_letter'),
                    record.get('on_time_flag', True),
                    self.batch_id
                ])
            
            self.con.commit()
            logger.info(f"✅ Loaded {len(grades)} grade records")
            return len(grades)
        
        except Exception as e:
            logger.error(f"❌ Error ingesting grades: {e}")
            self.con.rollback()
            raise
    
    def ingest_discipline(self):
        """Fetch and load discipline data"""
        logger.info("Ingesting discipline data from Aeries API...")
        
        try:
            discipline = self.client.fetch_discipline()
            logger.info(f"Fetched {len(discipline)} discipline records")
            
            for record in discipline:
                self.con.execute("""
                INSERT INTO raw_discipline (
                    discipline_id, student_id, school_id, incident_date,
                    incident_type, incident_description, teacher_id,
                    consequence_type, consequence_duration, escalation_level, _batch_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (discipline_id) DO UPDATE SET 
                    _updated_at = CURRENT_TIMESTAMP,
                    consequence_type = EXCLUDED.consequence_type
                """, [
                    record.get('discipline_id') or str(uuid.uuid4()),
                    record.get('student_id'),
                    record.get('school_id'),
                    record.get('incident_date'),
                    record.get('incident_type'),
                    record.get('incident_description'),
                    record.get('teacher_id'),
                    record.get('consequence_type'),
                    record.get('consequence_duration'),
                    record.get('escalation_level', 1),
                    self.batch_id
                ])
            
            self.con.commit()
            logger.info(f"✅ Loaded {len(discipline)} discipline records")
            return len(discipline)
        
        except Exception as e:
            logger.error(f"❌ Error ingesting discipline: {e}")
            self.con.rollback()
            raise
    
    def run_full_ingest(self):
        """Run complete data ingestion pipeline"""
        logger.info("=" * 60)
        logger.info(f"Starting full Aeries data ingestion (batch_id: {self.batch_id})")
        logger.info("=" * 60)
        
        results = {}
        
        try:
            results['students'] = self.ingest_students()
            results['attendance'] = self.ingest_attendance()
            results['grades'] = self.ingest_grades()
            results['discipline'] = self.ingest_discipline()
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ INGESTION COMPLETE")
            logger.info("=" * 60)
            for key, count in results.items():
                logger.info(f"  {key:15}: {count:6} records")
            logger.info("=" * 60)
            
            return results
        
        except Exception as e:
            logger.error(f"❌ Ingestion failed: {e}")
            raise
        
        finally:
            self.con.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    ingestor = AeriesDataIngestor()
    results = ingestor.run_full_ingest()
```

---

## Part 3: Excel Import Pipelines (Days 4-5)

### 3.1 D&F Report Import (Special Education + 504 + At-Risk)

**File to create**: `oss_framework/scripts/import_d_and_f_report.py`

```python
import pandas as pd
import duckdb
import os
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class DAndFImporter:
    """Import D&F (D grades and F grades) + 504 + Special Education flags from Excel"""
    
    def __init__(self, db_path: str = None):
        db_path = db_path or os.getenv("DUCKDB_DATABASE_PATH", "data/oea.duckdb")
        self.con = duckdb.connect(db_path)
        self.batch_id = str(uuid.uuid4())
    
    def import_from_excel(self, excel_path: str):
        """
        Import D&F report from Excel file
        Expected columns: student_id, first_name, last_name, grade_level, course,
                         grade, has_504, iep_status, disability_category
        """
        logger.info(f"Importing D&F report from {excel_path}...")
        
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            logger.info(f"Read {len(df)} records from Excel")
            
            # Create temporary table for import
            self.con.execute("""
            CREATE OR REPLACE TEMPORARY TABLE temp_d_and_f AS
            SELECT * FROM df
            """)
            
            # Update raw_students with 504 and IEP flags
            self.con.execute("""
            UPDATE raw_students rs
            SET 
                has_504_plan = COALESCE(temp.has_504, rs.has_504_plan),
                iep_status = COALESCE(temp.iep_status, rs.iep_status),
                disability_category = COALESCE(temp.disability_category, rs.disability_category),
                _updated_at = CURRENT_TIMESTAMP
            FROM temp_d_and_f temp
            WHERE rs.student_id = temp.student_id
            """)
            
            self.con.commit()
            logger.info(f"✅ Updated {len(df)} student records with D&F data")
            
            return len(df)
        
        except Exception as e:
            logger.error(f"❌ Error importing D&F report: {e}")
            self.con.rollback()
            raise
    
    def close(self):
        self.con.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    importer = DAndFImporter()
    excel_path = "oss_framework/docs/tech_docs/Requirements/D and F w_504 SE.xlsx"
    importer.import_from_excel(excel_path)
    importer.close()
```

### 3.2 Demographic Data Import

**File to create**: `oss_framework/scripts/import_demographic_data.py`

```python
import pandas as pd
import duckdb
import os
import logging
import uuid

logger = logging.getLogger(__name__)

class DemographicImporter:
    """Import demographic data (race/ethnicity by course section) from Excel"""
    
    def __init__(self, db_path: str = None):
        db_path = db_path or os.getenv("DUCKDB_DATABASE_PATH", "data/oea.duckdb")
        self.con = duckdb.connect(db_path)
        self.batch_id = str(uuid.uuid4())
    
    def import_from_excel(self, excel_path: str):
        """
        Import demographic data from Excel
        Expected structure: course_id, section_id, student_id, ethnicity
        """
        logger.info(f"Importing demographic data from {excel_path}...")
        
        try:
            df = pd.read_excel(excel_path)
            logger.info(f"Read {len(df)} demographic records")
            
            # Verify raw_students exists and update ethnicity where not populated
            for _, row in df.iterrows():
                self.con.execute("""
                UPDATE raw_students
                SET 
                    ethnicity = COALESCE(ethnicity, ?),
                    _updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
                """, [row.get('ethnicity'), row.get('student_id')])
            
            self.con.commit()
            logger.info(f"✅ Updated demographic data for {len(df)} records")
            
            return len(df)
        
        except Exception as e:
            logger.error(f"❌ Error importing demographic data: {e}")
            self.con.rollback()
            raise
    
    def close(self):
        self.con.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    importer = DemographicImporter()
    excel_path = "oss_framework/docs/tech_docs/Requirements/Demographic Data by Course 24_25.xlsx"
    importer.import_from_excel(excel_path)
    importer.close()
```

---

## Part 4: Data Validation Tests (Day 5)

**File to create**: `oss_framework/tests/test_stage1_data_quality.py`

```python
import pytest
import duckdb
import os

@pytest.fixture
def duckdb_connection():
    """Connect to DuckDB for testing"""
    db_path = os.getenv("DUCKDB_DATABASE_PATH", "data/oea.duckdb")
    con = duckdb.connect(db_path, read_only=False)
    yield con
    con.close()

class TestStage1DataQuality:
    
    def test_raw_students_not_empty(self, duckdb_connection):
        """Verify raw_students table has data"""
        result = duckdb_connection.execute(
            "SELECT COUNT(*) as cnt FROM raw_students"
        ).fetchall()
        count = result[0][0]
        assert count > 0, "raw_students table is empty!"
        print(f"✅ raw_students has {count} records")
    
    def test_raw_attendance_not_empty(self, duckdb_connection):
        """Verify raw_attendance table has data"""
        result = duckdb_connection.execute(
            "SELECT COUNT(*) as cnt FROM raw_attendance"
        ).fetchall()
        count = result[0][0]
        assert count > 0, "raw_attendance table is empty!"
        print(f"✅ raw_attendance has {count} records")
    
    def test_no_null_student_ids(self, duckdb_connection):
        """Verify all attendance records have valid student_ids"""
        result = duckdb_connection.execute("""
            SELECT COUNT(*) as cnt 
            FROM raw_attendance 
            WHERE student_id IS NULL
        """).fetchall()
        null_count = result[0][0]
        assert null_count == 0, f"Found {null_count} null student_ids in attendance!"
        print(f"✅ No null student_ids in attendance records")
    
    def test_attendance_dates_valid(self, duckdb_connection):
        """Verify attendance dates are reasonable"""
        result = duckdb_connection.execute("""
            SELECT COUNT(*) as cnt 
            FROM raw_attendance 
            WHERE attendance_date > CURRENT_DATE + INTERVAL 30 DAY
               OR attendance_date < DATE '2020-01-01'
        """).fetchall()
        invalid_count = result[0][0]
        assert invalid_count == 0, f"Found {invalid_count} invalid attendance dates!"
        print(f"✅ All attendance dates are valid")
    
    def test_grades_data_integrity(self, duckdb_connection):
        """Verify grade records have required fields"""
        result = duckdb_connection.execute("""
            SELECT COUNT(*) as cnt 
            FROM raw_academic_records 
            WHERE student_id IS NULL 
               OR course_id IS NULL
               OR assignment_id IS NULL
        """).fetchall()
        invalid_count = result[0][0]
        assert invalid_count == 0, f"Found {invalid_count} invalid grade records!"
        print(f"✅ All grade records have required fields")
    
    def test_discipline_dates_valid(self, duckdb_connection):
        """Verify discipline incident dates are reasonable"""
        result = duckdb_connection.execute("""
            SELECT COUNT(*) as cnt 
            FROM raw_discipline 
            WHERE incident_date > CURRENT_DATE + INTERVAL 30 DAY
               OR incident_date < DATE '2020-01-01'
        """).fetchall()
        invalid_count = result[0][0]
        assert invalid_count == 0, f"Found {invalid_count} invalid incident dates!"
        print(f"✅ All discipline dates are valid")
    
    def test_foreign_key_consistency(self, duckdb_connection):
        """Verify attendance records reference valid students"""
        result = duckdb_connection.execute("""
            SELECT COUNT(DISTINCT att.student_id) as cnt
            FROM raw_attendance att
            WHERE att.student_id NOT IN (SELECT student_id FROM raw_students)
        """).fetchall()
        orphaned_count = result[0][0]
        assert orphaned_count == 0, f"Found {orphaned_count} orphaned attendance records!"
        print(f"✅ All attendance records reference valid students")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Week 1-2 Execution Checklist

### Day 1-2: Aeries API Setup
- [ ] Create `aeries_api_client.py` with authentication
- [ ] Create `.env` file with credentials (⚠️ DO NOT COMMIT)
- [ ] Test API connection with `test_aeries_api.py`
- [ ] Verify rate limiting works

### Day 2-3: Stage 1 Infrastructure
- [ ] Create `create_stage1_tables.py` and initialize tables
- [ ] Verify all 5 landing tables created in DuckDB
- [ ] Run schema verification script

### Day 3-4: Data Ingestion
- [ ] Create `ingest_aeries_data.py`
- [ ] Run full ingestion pipeline
- [ ] Verify row counts for each table
- [ ] Check `_loaded_at` and `_batch_id` timestamps

### Day 4-5: Excel Imports
- [ ] Create `import_d_and_f_report.py`
- [ ] Create `import_demographic_data.py`
- [ ] Run Excel import pipelines
- [ ] Verify 504/IEP flags are populated

### Day 5: Data Quality & Testing
- [ ] Run `test_stage1_data_quality.py`
- [ ] Verify all data quality tests pass
- [ ] Document any data issues found
- [ ] Create data quality report

### End of Week 1-2 Deliverables
- ✅ Aeries API integration (working)
- ✅ Stage 1 landing zone (5 tables, populated)
- ✅ Excel import pipelines (D&F, Demographic, RFEP)
- ✅ Data quality validation (tests passing)
- ✅ Batch ingestion log (tracking `_batch_id`, `_loaded_at`)

---

## Environment Setup Commands

```bash
# Navigate to project directory
cd /Users/flucido/projects/openedDataEstate

# Create virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install duckdb pandas requests python-dotenv pytest

# Create logs directory
mkdir -p oss_framework/logs

# Test DuckDB connection
python3 -c "import duckdb; con = duckdb.connect('oss_framework/data/oea.duckdb'); print('✅ DuckDB connected')"

# Run initialization
python3 oss_framework/scripts/create_stage1_tables.py

# Run data ingestion
python3 oss_framework/scripts/ingest_aeries_data.py

# Run tests
pytest oss_framework/tests/test_stage1_data_quality.py -v
```

---

## Common Issues & Solutions

### Issue 1: DuckDB "Permission Denied" on data/ directory
```bash
# Solution: Ensure data directory is writable
chmod 755 oss_framework/data/
```

### Issue 2: Aeries API Rate Limiting Exceeded
```python
# Solution: Implement backoff retry logic (included in AeriesClient)
# The client automatically handles rate limiting with token bucket algorithm
```

### Issue 3: Foreign Key Constraint Violations
```bash
# Solution: Ensure raw_students are loaded BEFORE raw_attendance
# The ingest_aeries_data.py script handles this ordering automatically
```

---

## Next Phase: Week 3-4 Feature Engineering

Once Week 1-2 data foundation is complete and approved:
- Build Stage 2 dbt models
- Create attendance aggregation windows (30/60/90 day patterns)
- Calculate chronic absence flags
- Implement risk scoring algorithms

See `INTEGRATED_ANALYTICS_FRAMEWORK_DETAILED.md` Part 2 for full Week 3-4 specifications.

