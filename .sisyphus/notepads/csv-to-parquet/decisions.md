# Key Decisions for CSV-to-Parquet Conversion Script

## Decision 1: Chunking Strategy
**Decision:** Use file size threshold to auto-decide chunking
**Rationale:** 
- Files < 500MB: Single read (faster, simpler)
- Files > 500MB: Chunked read (prevents OOM)
**Implementation:** `use_chunking = file_size_mb > 500`

## Decision 2: Student ID Handling
**Decision:** ALWAYS use dtype={'student_id': str, 'school_id': str}
**Rationale:** 
- Prevents leading zero loss (010816 → 10816)
- Prevents join failures
- Industry standard for education data pipelines
**Source:** Multiple StackOverflow posts, pandas docs

## Decision 3: ZSTD Compression Level
**Decision:** Use compression_level=5 for all files
**Rationale:**
- Sweet spot: 70-75% of max compression, 3x faster writes than level 10
- Local analytics don't need max compression
- Benchmarks show diminishing returns after level 7
**Source:** Medium "10 Pandas IO Optimizations", StackOverflow #79627670

## Decision 4: Date Parsing Strategy
**Decision:** Parse dates AFTER read_csv, not during
**Rationale:**
- Aeries exports have mixed date formats
- parse_dates parameter can fail silently
- errors='coerce' allows validation of failures
**Implementation:** 
```python
df = pd.read_csv(file, dtype={'date': str})
df['date'] = pd.to_datetime(df['date'], errors='coerce')
print(f"Invalid dates: {df['date'].isna().sum()}")
```

## Decision 5: Categorical Dtypes
**Decision:** Use 'category' for attendance codes, school names, grade levels
**Rationale:**
- 10-50x memory reduction for repeated values
- Faster filtering/grouping operations
- Parquet preserves categorical encoding
**Columns to categorize:**
- attendance_code (Present/Absent/Tardy/Excused)
- school_name (~20 unique values)
- grade_level (K-12)

## Decision 6: Validation Strategy
**Decision:** Use DuckDB for post-conversion validation
**Rationale:**
- Faster than pandas for row counts on large parquet files
- Can validate without loading full file into memory
- Already in dependency stack
**Validation checks:**
1. Row count match (CSV == Parquet)
2. Schema inspection (types preserved)
3. Spot check sample rows

## Decision 7: Engine Choice
**Decision:** Use pyarrow engine (not fastparquet)
**Rationale:**
- Faster multithreaded writes
- Better ZSTD compression
- More actively maintained
- Compatible with DuckDB, Spark, Polars
**Source:** PyArrow docs, pandas performance comparisons

## Decision 8: Memory Monitoring
**Decision:** Log memory usage at key checkpoints
**Rationale:**
- Helps diagnose OOM issues
- Provides baseline for future optimizations
- Low overhead (psutil)
**Checkpoints:**
- Start
- After read_csv
- After to_parquet
- After cleanup

