# Known Issues and Gotchas for CSV-to-Parquet Conversion

## CRITICAL ISSUES (Must Address)

### 1. Student ID Leading Zeros Loss
**Impact:** HIGH - Data corruption, join failures
**Cause:** pandas infers numeric dtype, strips leading zeros from "010816"
**Solution:** `dtype={'student_id': str}` in read_csv()
**Evidence:** StackOverflow #16929056, #13250046 - widespread issue with education data

### 2. Memory Exhaustion on 12M Row File
**Impact:** HIGH - Script will crash on grades.csv
**Cause:** 12M rows * mixed dtypes = 12-24GB RAM usage
**Solution:** Use `chunksize=100_000` parameter or explicit dtypes
**Evidence:** pandas docs confirm full load even with low_memory=True

### 3. Mixed Type Inference (low_memory=True gotcha)
**Impact:** MEDIUM - Inconsistent data types across chunks
**Cause:** low_memory=True processes in chunks, can infer different types
**Solution:** Always specify dtype dictionary explicitly
**Evidence:** pandas documentation warning

## MINOR ISSUES (Good to Know)

### 4. Date Format Variations in Aeries Exports
**Impact:** MEDIUM - Silent date parsing failures
**Cause:** Mix of MM/DD/YYYY and YYYY-MM-DD in same file
**Solution:** Parse dates separately with errors='coerce'

### 5. Compression Level Overkill
**Impact:** LOW - Slower writes for minimal space savings
**Cause:** Using compression_level=10+ is unnecessary for local analytics
**Solution:** Use compression_level=5 (sweet spot)
**Evidence:** Medium article benchmarks show diminishing returns after level 7

### 6. Categorical Dtype Forgotten
**Impact:** LOW - Higher memory usage than needed
**Cause:** Not using 'category' dtype for repeated values
**Solution:** Use dtype={'attendance_code': 'category'}
**Evidence:** 10-50x memory reduction for columns with <100 unique values

## VALIDATION GAPS

### 7. No Row Count Verification
**Impact:** MEDIUM - Silent data loss undetected
**Solution:** Use DuckDB to verify CSV row count == Parquet row count

### 8. No Student ID Format Validation
**Impact:** MEDIUM - Invalid IDs slip through
**Solution:** Regex check `^\\d{6}$` after read_csv

## PERFORMANCE BOTTLENECKS

### 9. Single-Threaded CSV Parsing
**Impact:** LOW - Can't speed up CSV read beyond pandas limitations
**Note:** pyarrow CSV reader is faster but less feature-complete

### 10. Memory Copies During Chunking
**Impact:** LOW - Chunked reads are ~2x slower than single read
**Trade-off:** Acceptable for preventing OOM on large files

