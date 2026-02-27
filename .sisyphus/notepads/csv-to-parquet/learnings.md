# CSV to Parquet Conversion Research - Best Practices for Education Data

**Research Date:** 2026-02-26
**Context:** Converting large CSV files (852 rows to 12M rows) to Parquet with pandas/pyarrow
**Focus:** Education data with PII, memory optimization, data validation

---

## 1. PANDAS read_csv() MEMORY OPTIMIZATION

### Critical Parameters for Large Files

**dtype Specification (HIGHEST PRIORITY for education data)**
```python
# Specify dtypes upfront to prevent:
# - Memory bloat from object dtype inference
# - Leading zero loss in student IDs
# - Mixed type columns

dtype = {
    'student_id': str,          # Prevents 010816 → 10816
    'school_id': str,           # Same issue
    'grade_level': 'Int16',     # Small integers (K-12 = 0-12)
    'attendance_code': 'category',  # Repeating values
    'date': str,                # Parse separately with pd.to_datetime()
}

df = pd.read_csv('attendance.csv', dtype=dtype)
```

**Evidence:** 
- Source: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- Leading zeros are a KNOWN ISSUE with student IDs (StackOverflow #16929056, #13250046)
- dtype=str preserves "010816" format, then convert later if needed
- Memory savings: int64 → int16 cuts memory in half for grade columns

### Chunking Strategy for Multi-Million Row Files

**When to use chunking:**
- File size > 1-2GB
- Available RAM < 3x file size
- Processing can be done incrementally

```python
# For 12M row grades file:
chunk_size = 100_000  # 100K rows per chunk
chunks = []

for chunk in pd.read_csv('grades.csv', chunksize=chunk_size, dtype=dtype_spec):
    # Process chunk (filter, transform, etc.)
    processed = chunk[chunk['grade'] != 'N/A']
    chunks.append(processed)

df = pd.concat(chunks, ignore_index=True)
```

**Trade-offs:**
- Pros: Prevents OOM, allows progress monitoring
- Cons: Slower than single read, can't use operations requiring full dataset
- Evidence: pandas docs "Iteration" section, context7 documentation

### low_memory Flag GOTCHA

```python
# DON'T rely on default low_memory=True
# It processes in chunks but ENTIRE file still loaded into ONE DataFrame
# Can cause mixed-type inference issues

# BETTER: Explicitly set dtype OR use chunksize for true memory control
df = pd.read_csv('file.csv', dtype=dtype_spec, low_memory=False)
```

**Evidence:** pandas documentation warns: "entire file is read into a single DataFrame regardless"

---

## 2. COMMON ERRORS WITH EDUCATION DATA

### Student ID Leading Zeros (CRITICAL)

**Problem:** Student IDs like "001234" or "010816" (birthday-based) lose leading zeros
**Impact:** Joins fail, lookups break, PII exposure risk increases
**Solution:**
```python
dtype = {'student_id': str, 'school_id': str}
df = pd.read_csv('students.csv', dtype=dtype, converters={'student_id': str})
```

**Alternative for existing DataFrame:**
```python
# If already imported incorrectly:
df['student_id'] = df['student_id'].astype(str).str.zfill(6)  # Pad to 6 digits
```

### Date Parsing Issues (Aeries/SIS exports)

**Problem:** Date formats vary across Aeries exports (MM/DD/YYYY vs YYYY-MM-DD)
**Solution:**
```python
# Don't use parse_dates at read time - too risky with mixed formats
df = pd.read_csv('attendance.csv', dtype={'date_field': str})

# Parse separately with error handling
df['date'] = pd.to_datetime(df['date_field'], errors='coerce', format='%m/%d/%Y')
# Check for coercion failures
print(f"Invalid dates: {df['date'].isna().sum()}")
```

### Categorical Data for Memory Savings

**Use case:** Attendance codes, grade levels, school names (repeated values)
```python
dtype = {
    'attendance_code': 'category',  # "Present", "Absent", "Tardy" (3 unique values)
    'school_name': 'category',       # 20 schools vs 3.5M rows
}

# Memory savings: 50-100MB (object) → 1-5MB (category) per column
```

**Evidence:** Pandas memory comparison table shows 10-50x reduction for categorical

---

## 3. PARQUET WRITE OPTIMIZATION

### ZSTD Compression Settings

**Recommended for analytics workloads:**
```python
df.to_parquet(
    'output.parquet',
    engine='pyarrow',
    compression='zstd',
    compression_level=5,  # Sweet spot for analytics
    index=False
)
```

**Compression Level Trade-offs:**
- Level 1-3: Fast write, larger files (~2x faster, 20% larger)
- Level 5-7: Balanced (RECOMMENDED for local analytics)
- Level 10+: Slow write, best compression (overkill for local use)

**Evidence:**
- StackOverflow #79627670: pandas zstd level 10 gives 28-33% better compression than Spark
- Medium article "10 Pandas IO Optimizations": level 5-7 is sweet spot for analytics
- PyArrow docs confirm ZSTD as best compression for query performance

**Expected compression ratios:**
- CSV 350KB → Parquet ~100-150KB (students, mostly text)
- CSV 2GB → Parquet ~400-600MB (attendance, numeric + categorical)
- CSV 8GB → Parquet ~1.5-2.5GB (grades, mixed data)

### Arrow Engine Benefits

```python
# Use pyarrow for ALL parquet operations
import pyarrow.parquet as pq
import pyarrow as pa

# Option 1: Direct pandas
df.to_parquet('output.parquet', engine='pyarrow', compression='zstd')

# Option 2: Arrow table (more control)
table = pa.Table.from_pandas(df)
pq.write_table(table, 'output.parquet', compression='zstd', compression_level=5)
```

**Why pyarrow over fastparquet:**
- Faster writes (multithreaded)
- Better compression
- Active development, used by Spark/Dask

---

## 4. DATA VALIDATION STRATEGIES

### Pre-Conversion Validation

```python
import pandas as pd

# 1. Check expected columns exist
expected_cols = ['student_id', 'date', 'attendance_code']
df = pd.read_csv('attendance.csv', dtype={'student_id': str})
missing = set(expected_cols) - set(df.columns)
if missing:
    raise ValueError(f"Missing columns: {missing}")

# 2. Check row count makes sense
if len(df) < 1000:  # Attendance should have thousands of rows
    print(f"WARNING: Only {len(df)} rows, expected more")

# 3. Check for completely empty columns
empty_cols = df.columns[df.isna().all()].tolist()
if empty_cols:
    print(f"Empty columns (will drop): {empty_cols}")
    df = df.drop(columns=empty_cols)

# 4. Check student ID format (should be 6 digits after cleaning)
invalid_ids = df[~df['student_id'].str.match(r'^\d{6}$', na=False)]
if len(invalid_ids) > 0:
    print(f"WARNING: {len(invalid_ids)} invalid student IDs")
```

### Post-Conversion Validation (with DuckDB)

```python
import duckdb

# 1. Row count verification
csv_count = len(pd.read_csv('students.csv', usecols=[0]))  # Just first col
parquet_count = duckdb.query("SELECT COUNT(*) FROM 'students.parquet'").fetchone()[0]

assert csv_count == parquet_count, f"Row mismatch: {csv_count} vs {parquet_count}"

# 2. Check data types preserved
schema = duckdb.query("DESCRIBE SELECT * FROM 'students.parquet'").df()
print(schema)

# 3. Spot check values
sample = duckdb.query("""
    SELECT student_id, first_name 
    FROM 'students.parquet' 
    LIMIT 5
""").df()
print(sample)
```

### Memory Monitoring During Conversion

```python
import psutil
import os

process = psutil.Process(os.getpid())

def log_memory(label):
    mem = process.memory_info().rss / 1024 / 1024  # MB
    print(f"{label}: {mem:.1f} MB")

log_memory("Start")
df = pd.read_csv('large_file.csv', dtype=dtype_spec)
log_memory("After read_csv")
df.to_parquet('output.parquet', compression='zstd')
log_memory("After to_parquet")
del df
log_memory("After cleanup")
```

---

## 5. PII HANDLING CONSIDERATIONS

### Education Data Privacy Best Practices

**DO:**
- Keep student_id as string dtype (prevents accidental sorting/display issues)
- Use categorical dtype for sensitive but repeated data (school names)
- Validate no PII in parquet metadata (pandas doesn't add by default)
- Compress with ZSTD to reduce file size (smaller attack surface)

**DON'T:**
- Don't include student names in attendance/grades files if IDs suffice
- Don't log sample data during debugging (use .head() cautiously)
- Don't write parquet files to shared directories without access controls

**Validation check:**
```python
# Check parquet metadata doesn't contain PII
import pyarrow.parquet as pq
metadata = pq.read_metadata('students.parquet')
print(metadata.metadata)  # Should be None or minimal
```

---

## 6. EXPECTED PERFORMANCE BENCHMARKS

Based on research and similar workloads:

**Students (852 rows, ~350KB CSV):**
- read_csv: < 0.1s
- to_parquet: < 0.1s
- Compression ratio: 2-3x
- Memory usage: < 10MB

**Attendance (3.5M rows, est. 2GB CSV):**
- read_csv (with dtype): 5-15s
- read_csv (chunked): 10-30s (but safer)
- to_parquet: 10-20s
- Compression ratio: 4-5x
- Peak memory: 4-8GB (full load) or 1-2GB (chunked)

**Grades (12M rows, est. 6-8GB CSV):**
- read_csv (with dtype): 20-60s
- read_csv (chunked): RECOMMENDED (60-120s but won't OOM)
- to_parquet: 30-60s
- Compression ratio: 3-4x
- Peak memory: 12-24GB (full) or 2-4GB (chunked)

**System Requirements (macOS darwin):**
- Minimum RAM: 8GB (with chunking)
- Recommended RAM: 16GB
- Disk space: 3x largest CSV file

---

## 7. COMPLETE EXAMPLE SCRIPT

```python
import pandas as pd
import duckdb
import os

# Configuration
CSV_FILE = 'attendance.csv'
PARQUET_FILE = 'attendance.parquet'
CHUNK_SIZE = 100_000  # Adjust based on available memory

# Step 1: Define dtypes (CRITICAL for student IDs)
dtype_spec = {
    'student_id': str,
    'school_id': str,
    'date': str,  # Parse separately
    'attendance_code': 'category',
    'period': 'Int8',  # -128 to 127
}

# Step 2: Decide on chunking
file_size_mb = os.path.getsize(CSV_FILE) / 1024 / 1024
use_chunking = file_size_mb > 500  # Use chunks if > 500MB

if use_chunking:
    print(f"File size {file_size_mb:.1f}MB - using chunked read")
    chunks = []
    for i, chunk in enumerate(pd.read_csv(CSV_FILE, chunksize=CHUNK_SIZE, dtype=dtype_spec)):
        # Parse dates
        chunk['date'] = pd.to_datetime(chunk['date'], errors='coerce', format='%m/%d/%Y')
        chunks.append(chunk)
        if (i + 1) % 10 == 0:
            print(f"Processed {(i + 1) * CHUNK_SIZE:,} rows")
    
    df = pd.concat(chunks, ignore_index=True)
else:
    print(f"File size {file_size_mb:.1f}MB - single read")
    df = pd.read_csv(CSV_FILE, dtype=dtype_spec)
    df['date'] = pd.to_datetime(df['date'], errors='coerce', format='%m/%d/%Y')

# Step 3: Validate
print(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB")

# Step 4: Write to Parquet
df.to_parquet(
    PARQUET_FILE,
    engine='pyarrow',
    compression='zstd',
    compression_level=5,
    index=False
)

# Step 5: Verify with DuckDB
csv_count = len(df)
parquet_count = duckdb.query(f"SELECT COUNT(*) FROM '{PARQUET_FILE}'").fetchone()[0]
assert csv_count == parquet_count, f"Row count mismatch!"

print(f"✓ Conversion complete: {csv_count:,} rows validated")
print(f"✓ File size: {os.path.getsize(PARQUET_FILE) / 1024 / 1024:.1f} MB")
```

---

## 8. KEY TAKEAWAYS

1. **ALWAYS specify dtype for student/school IDs** (dtype={'student_id': str})
2. **Use chunking for files > 500MB** or when RAM < 3x file size
3. **ZSTD compression level 5** is the sweet spot for local analytics
4. **Validate row counts** with DuckDB after conversion
5. **Parse dates separately** (don't trust parse_dates with mixed formats)
6. **Use categorical dtype** for repeated values (attendance codes, schools)
7. **low_memory=True is misleading** - doesn't prevent full load, just changes inference
8. **pyarrow engine** is faster and better supported than fastparquet

---

## SOURCES

- pandas.pydata.org/docs/reference/api/pandas.read_csv.html (memory optimization docs)
- arrow.apache.org/docs/python/parquet.html (compression recommendations)
- Context7 pandas documentation (chunking examples)
- StackOverflow #16929056, #13250046 (student ID leading zeros)
- StackOverflow #79627670 (ZSTD compression comparison)
- Medium "8 Pandas Performance Hacks for 2026"
- Medium "10 Pandas IO Optimizations (Parquet/Arrow/ZSTD)"

