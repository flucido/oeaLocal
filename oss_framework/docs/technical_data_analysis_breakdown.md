# OEA Technical Data Analysis Breakdown
## For Data Experts & Analytics Professionals

**Purpose:** Transparent, peer-reviewable documentation of analytical approaches used in OEA packages and modules  
**Audience:** Data scientists, statisticians, analytics leads, audit committees  
**Scope:** Methods, validation, limitations, and reproducibility for each major use case

---

## Executive Summary for Technical Reviewers

OEA implements education analytics using industry-standard, peer-reviewed methodologies. This document provides:

1. **Analytical Framework** - What methods we use and why
2. **Data Quality & Validation** - How we ensure data integrity
3. **Statistical Rigor** - Assumptions, testing, and limitations
4. **Model Validation** - Cross-validation, holdout testing, performance metrics
5. **Fairness & Bias Assessment** - How we evaluate model equity across demographics
6. **Reproducibility** - How to audit and replicate analyses
7. **Specific Use Case Breakdowns** - Technical details for each major package

---

## Part 1: Foundational Analytical Framework

### 1.1 Overall Analysis Architecture

OEA follows the **medallion lakehouse pattern** with deliberate analytical tiers:

```
┌─────────────────────────────────────────────────────┐
│ STAGE 1: RAW DATA INGESTION                         │
│ ├─ Source data loaded as-received (Parquet format) │
│ ├─ No transformations applied                       │
│ ├─ Audit trail retained (when/how loaded)          │
│ └─ Purpose: Preserve original data for replication │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ STAGE 2: DATA REFINEMENT (Reproducible, Auditable) │
│ ├─ Data typing (dates, categories, numerics)       │
│ ├─ Validation rules (domain constraints)           │
│ ├─ Outlier detection & handling (documented)       │
│ ├─ Missing data imputation (method-specific)       │
│ ├─ PII pseudonymization (deterministic hashing)    │
│ ├─ dbt tests (schema, data, referential integrity) │
│ └─ Purpose: Analytics-ready data with audit trail  │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ STAGE 3: FEATURE ENGINEERING                        │
│ ├─ Domain-specific feature creation                │
│ ├─ Temporal features (trends, seasonality)         │
│ ├─ Aggregations (rolling averages, counts)         │
│ ├─ Encoding (categorical variables)                │
│ ├─ Scaling (standardization if needed)             │
│ └─ Purpose: Predictive power for modeling          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ STAGE 4: MODEL DEVELOPMENT & VALIDATION             │
│ ├─ Algorithm selection (justified by use case)      │
│ ├─ Hyperparameter tuning (grid/random search)      │
│ ├─ Cross-validation (time-aware if temporal)       │
│ ├─ Holdout test set (stratified sampling)          │
│ ├─ Fairness assessment (demographic parity)        │
│ └─ Purpose: Validated, fair predictions            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│ STAGE 5: EXPLAINABILITY & DEPLOYMENT                │
│ ├─ Feature importance (SHAP values)                │
│ ├─ Prediction explanations (why flagged)           │
│ ├─ Monitoring setup (drift detection)              │
│ ├─ Refresh schedule (retraining frequency)         │
│ └─ Purpose: Interpretable, maintainable decisions  │
└─────────────────────────────────────────────────────┘
```

### 1.2 Analytical Philosophy

**Guiding Principles:**

1. **Transparency Over Accuracy Alone**
   - We prioritize interpretability so educators understand *why* a student is flagged
   - A 85% accurate, explainable model is better than 92% accurate black-box

2. **Fairness By Design**
   - All models tested for disparate impact across demographics
   - Fairness constraints built into model selection, not post-hoc

3. **Reproducibility First**
   - All analyses in code (not Excel), version controlled
   - Random seeds fixed for determinism
   - dbt documentation ensures exact replication

4. **Domain Expertise Embedded**
   - Features designed with education researchers (not just statistical optimization)
   - Domain constraints incorporated (e.g., can't have negative attendance)

5. **Conservative Predictions**
   - When uncertain, flag for review rather than recommend action
   - Better to identify 20 students manually than miss 1 truly at-risk student

---

## Part 2: Data Quality & Validation Framework

### 2.1 Validation Tiers

**Tier 1: Schema Validation** (Automated, on ingest)
```sql
-- Example: Attendance data validation
dbt test on attendance_schema:
  ├─ not_null(student_id): All students have ID
  ├─ not_null(attendance_date): All dates recorded
  ├─ unique_combination(student_id, attendance_date): No duplicates
  ├─ accepted_values(status, ['Present', 'Absent', 'Excused', 'Tardy'])
  ├─ relationships(student_id → student_master.student_id): Referential integrity
  └─ column_type_check(attendance_date = DATE): Type validation
```

**Tier 2: Domain Validation** (Business logic)
```
Attendance-specific rules:
├─ attendance_rate BETWEEN 0 AND 1 (no >100% or <0%)
├─ attendance_date >= cohort_start_date
├─ attendance_date <= TODAY()
├─ For each student: present + absent + excused = total_days_in_period
└─ Alert if >5% of records fail domain rules (data quality issue)
```

**Tier 3: Statistical Validation** (Anomaly detection)
```
Outlier detection (Isolation Forest):
├─ Identify unusual attendance patterns (e.g., student 3σ below median)
├─ Flag data entry errors (same value for 100 days in a row)
├─ Detect anomalies in LMS engagement (spikes/drops >150% from trend)
├─ Manual review process for high-impact outliers
└─ Document handling method (imputation, flagging, or exclusion)
```

**Tier 4: Cross-System Validation** (Coherence checking)
```
Attendance + LMS Cross-Check:
├─ Students marked absent shouldn't have LMS login same day (OR has reason)
├─ Chronic absence + zero engagement = high confidence in at-risk flag
├─ Discrepancies logged for manual review
└─ If <85% coherence with another system, escalate to data steward
```

### 2.2 Missing Data Strategy

**Philosophy:** Transparent handling, not silent exclusion

```
Missing Data Handling by Type:

1. MCAR (Missing Completely at Random)
   ├─ Deletion threshold: <5% missing
   ├─ Method: Listwise deletion (remove row)
   └─ Rationale: Minimal bias, safe to exclude

2. MAR (Missing at Random)
   ├─ Example: Attendance missing only when student absent (not recorded)
   ├─ Method: Multiple imputation (5 imputations, pool results)
   ├─ OR: Indicator variable (flag missingness as feature)
   └─ Rationale: Preserves relationships, captures pattern

3. MNAR (Missing Not at Random)
   ├─ Example: High-performing students skip recording attendance
   ├─ Method: Sensitivity analysis (impute low, impute high, compare results)
   └─ Rationale: Assess if conclusions change under different assumptions

4. Structural Missingness
   ├─ Example: New student, no prior attendance data
   ├─ Method: Separate model or impute from similar peers
   └─ Rationale: Avoid penalizing recent arrivals
```

**Documentation:** For every missing data instance >1%, we document:
- Percentage missing by variable and time period
- Method used (deletion/imputation/flagging)
- Sensitivity analysis (if applicable)
- Confidence intervals adjusted for imputation uncertainty

---

## Part 3: Statistical Rigor & Assumptions

### 3.1 Chronic Absenteeism Prediction Model

**Use Case:** Identify students at risk of chronic absence (>10% of days absent)

#### Problem Formulation
```
Binary Classification Problem:
  Input: Student demographic + attendance + engagement + barriers (t-1)
  Output: Will student be chronically absent in next period? (Yes/No)
  
Temporal Structure:
  ├─ Training: September to December (4 months)
  ├─ Prediction target: January to April (next 4 months)
  ├─ Holdout test: May to June (validation period)
  └─ No information leakage (always predict forward in time)
```

#### Data Requirements & Assumptions

| Assumption | How We Validate | Risk if Violated |
|---|---|---|
| **Temporal Independence** - Each student's outcome is independent | Clusters standard errors by school | Overconfident confidence intervals |
| **Stationarity** - Absence patterns don't change fundamentally over years | Seasonal decomposition + trend test | Model doesn't generalize to new years |
| **Completeness** - We capture >90% of absences | Compare SIS to school calendar/payroll | Underestimate absence |
| **Labeling Consistency** - Chronic absence defined same way all schools | Audit 50 records per school | Inconsistent training signal |
| **Feature Stability** - Engagement platforms log same way | Validate API schemas, test data freshness | Features unstable over time |

#### Feature Selection & Engineering

**Base Features (No Aggregation):**
```
Student Demographics:
├─ Grade level (categorical: K–12)
├─ Special education status (binary)
├─ English learner status (binary)
├─ Socioeconomic status indicator (if available)
├─ Transportation type (walk/bus/drive)
└─ Known barriers flagged (health, housing, etc.)

Attendance Signals:
├─ Days absent in past 20 days (count)
├─ Days absent in past 60 days (count)
├─ Absence rate (%) in past 60 days
├─ Absence trend (linear regression slope)
├─ Absence variance (high = erratic pattern)
└─ Days since last absence (continuity signal)

Engagement Signals:
├─ LMS logins in past 20 days (count)
├─ Assignment submissions in past 20 days (count)
├─ Days with zero engagement (count)
├─ Engagement trend (linear slope)
├─ Course-specific engagement (by subject)
└─ Device type (indicates access barriers)

Environmental Signals:
├─ School-level absence rate (contextual)
├─ Grade-level absence rate (contextual)
├─ Seasonal indicator (month: winter breaks, spring break)
└─ School calendar events (standardized testing, holidays)
```

**Feature Rationale (Why Each Feature):**

| Feature | Education Research Basis | Data Source |
|---|---|---|
| **Absence trend** | Research shows acceleration is early warning signal (not just current rate) | SIS attendance history |
| **Engagement (LMS)** | Disengaged students more likely to stop attending | LMS logs |
| **Days with zero engagement** | Complete absence from all digital channels is strong signal | Multi-platform engagement |
| **Barriers flagged** | IEP, health issues, known housing instability are documented predictors | Student information system |
| **School-level context** | Addresses school resource differences; contextualizes individual data | Aggregated by school |
| **Temporal lag** | Always use past data to predict future (no leakage) | t-1 to t-4 for prediction of t+1 to t+4 |

**Feature Engineering Decisions:**
```
Rationale for specific transformations:

1. Why Trend (slope) not just current rate?
   └─ Getting worse is more predictive than just being bad
   └─ Validates with research on acceleration indicators

2. Why separate engagement signals (LMS + barriers)?
   └─ Can have engagement despite absence (e.g., online student)
   └─ Can have barriers despite good attendance (e.g., health but persistent)
   └─ Combined signal is stronger: (absence + zero engagement) = very high risk

3. Why include contextual features (school, grade level)?
   └─ Absence norms vary by school and grade
   └─ 8% absence is normal for high school, concerning for elementary
   └─ Fairness: don't penalize students in high-absence schools unfairly

4. Why no demographic weighting in features?
   └─ Fairness principle: use as features but monitor for disparate impact
   └─ If model relies *too heavily* on demographics, fairness test catches it
   └─ Prevents using demographics as proxy for other factors
```

#### Model Selection & Justification

**Algorithm: XGBoost Gradient Boosting**

```
Why XGBoost (not logistic regression, not deep learning)?

✓ ADVANTAGES:
  ├─ Handles non-linear relationships (absence + engagement interaction)
  ├─ Feature importance interpretable (SHAP values)
  ├─ Robust to outliers (tree-based)
  ├─ Fast to train and predict (important for dashboard refresh)
  ├─ Works well with mixed feature types (categorical + continuous)
  ├─ Can incorporate class weights (if imbalanced absence/no absence)
  └─ Extensive education sector validation (other districts using same approach)

✗ ALTERNATIVES CONSIDERED & REJECTED:
  ├─ Logistic Regression: Too linear; can't capture absence × engagement interaction
  ├─ Random Forest: Good, but XGBoost typically 2–5% more accurate
  ├─ SVM: Poor feature importance; slower prediction
  ├─ Deep Learning (Neural Nets): Black box; harder to explain to educators
  └─ Simple Rules (e.g., "if absence >10%, flag"): No; misses early warning signals
```

**Hyperparameter Settings:**
```python
XGBoost Configuration:
├─ max_depth = 5 (shallow trees → less overfitting, more interpretable)
├─ learning_rate = 0.05 (slow learning → better generalization)
├─ n_estimators = 100 (typically good, validated with early stopping)
├─ subsample = 0.8 (80% of rows per tree → reduces overfitting)
├─ colsample_bytree = 0.8 (80% of features per tree → reduces correlation)
├─ class_weight = 'balanced' (adjust for imbalanced classes if needed)
└─ scale_pos_weight = (n_negative / n_positive) (accounts for class imbalance)

Tuning Method:
├─ Grid search over learning_rate and max_depth
├─ 5-fold cross-validation (stratified)
├─ Optimize on F1-score (balances precision & recall)
└─ Validation against holdout test set
```

#### Cross-Validation Strategy

```
5-Fold Stratified Time-Series Cross-Validation:

Fold 1: Train on Sept–Oct,  Test on Nov
Fold 2: Train on Sept–Nov,  Test on Dec
Fold 3: Train on Sept–Dec,  Test on Jan
Fold 4: Train on Sept–Jan,  Test on Feb
Fold 5: Train on Sept–Feb,  Test on Mar

Why this approach?
├─ Stratified: Each fold has same % of chronically absent students
├─ Time-aware: Always train on past, test on future (respect temporal order)
├─ Progressive: Later folds include more training data (realistic)
└─ Multiple folds: Average performance across seasons (account for seasonality)

Alternative tested: Random CV
└─ Not used because it allows leakage (training on future data)
└─ Also ignores temporal patterns in absence
```

#### Performance Metrics & Interpretation

```
Primary Metrics (what educators care about):

1. SENSITIVITY (Recall) = TP / (TP + FN)
   ├─ "Of students actually at risk, how many do we catch?"
   ├─ Target: ≥85% (miss <15% of truly at-risk students)
   ├─ Rationale: False negatives are worse (miss at-risk student)
   └─ Validation: Manual review of missed students

2. PRECISION = TP / (TP + FP)
   ├─ "Of students we flag, how many are actually at-risk?"
   ├─ Target: ≥70% (accept some false alarms for safety)
   ├─ Rationale: False positives cost time but not harm
   └─ Validation: Educators report "this feels right"

3. F1-Score = 2 × (Precision × Recall) / (Precision + Recall)
   ├─ Harmonic mean balancing both
   ├─ Target: ≥0.77 (80% of model is "good" overall)
   └─ Used for hyperparameter tuning

Secondary Metrics (diagnostic):

4. ROC-AUC = Area Under Receiver Operating Characteristic Curve
   ├─ Insensitive to class imbalance (good for imbalanced data)
   ├─ Target: ≥0.85 (random = 0.50, perfect = 1.00)
   └─ Used to compare against baseline

5. Calibration Curve
   ├─ "If model says 70% risk, is it actually ~70% of students are absent?"
   ├─ Check: Plot predicted probability vs. actual outcome
   ├─ Adjust predictions if poorly calibrated
   └─ Important for threshold-setting decisions

Metrics NOT used:

❌ Accuracy (Class Imbalance)
   └─ If only 10% of students are at-risk, naive model predicting "not at-risk" 
      is 90% accurate but useless

❌ Specificity alone (Asymmetric Cost)
   └─ Catching 99% of non-at-risk students doesn't help us

❌ Lift (Marketing Metric)
   └─ Not relevant for educational outcomes
```

#### Fairness & Bias Assessment

```
FAIRNESS TESTING: Ensure model performs equitably across demographics

Test 1: Demographic Parity
────────────────────────────
Definition: Does model predict "at-risk" at same rate for all groups?
Formula: P(Pred=at-risk | Group=A) ≈ P(Pred=at-risk | Group=B)

Test for each demographic:
├─ Grade level (elementary vs. middle vs. high school)
├─ Special education (yes/no)
├─ English learner status (yes/no)
├─ Race/ethnicity (if available and non-violating)
├─ Gender (yes/no)
└─ Socioeconomic status (free/reduced lunch eligibility)

Acceptable range: Within ±5 percentage points
Example: If 15% of non-EL students flagged, should be 10–20% of EL students
If outside range: Model may have inherent bias

Remediation if bias found:
├─ Remove demographic features (if not predictive)
├─ Add fairness constraints in model training
├─ Threshold adjustment by group (non-standard; use cautiously)
└─ Re-baseline with different features

Test 2: Equalized Odds
──────────────────────
Definition: Does model have same True Positive Rate (TPR) and False Positive 
Rate (FPR) across groups?

Formula: 
├─ TPR_A = TP_A / (TP_A + FN_A)  should ≈ TPR_B
├─ FPR_A = FP_A / (FP_A + TN_A)  should ≈ FPR_B
└─ Tests that model accuracy is equitable

Why important: Ensures we're not missing at-risk students of certain groups

Test 3: Calibration Parity
──────────────────────────
Definition: For students flagged as 70% at-risk, is that 70% across all groups?

Method: Split students by demographic group, check calibration separately
Example: If model says 70% at-risk for Black students, are 70% actually at-risk?

Acceptable: Within ±10 percentage points
Ensures: Confidence in predictions is consistent across groups

DOCUMENTATION:
For each use case, we publish:
├─ Fairness test results table
├─ Any disparity identified and remediation taken
├─ Limitations (e.g., "model slightly favors [group]")
└─ Recommendation: Always use with human review, not automated decisions
```

---

## Part 4: Student Well-Being Prediction Model

**Use Case:** Identify students at risk of dropping out / needing support

### 4.1 Problem Formulation

```
Multivariate Risk Assessment (Not just one risk score):

Student Well-Being Risk includes:
├─ Academic Risk: Engagement + grades + completion
├─ Attendance Risk: Chronic absence + tardies
├─ Health Risk: Health flags + behavior incidents
├─ Social Risk: Demographic + known barriers
└─ Composite: Combined risk across all dimensions

Output: Risk profile by dimension (not single number)
├─ Academic: Low/Medium/High
├─ Attendance: Low/Medium/High
├─ Health: Low/Medium/High
├─ Social: Low/Medium/High
├─ Recommendation: Different interventions per dimension
```

### 4.2 Data Sources & Integration

```
Multi-Source Integration (Requires careful alignment):

Source 1: SIS (Student Information System)
├─ Demographic data (grade, enrollment status)
├─ Grades (GPA, transcript)
├─ Attendance (days absent, tardies)
├─ Flags (IEP, ELL, special programs)

Source 2: LMS (Learning Management System)
├─ Course enrollment
├─ Assignment submission rates
├─ Discussion forum participation
├─ Time spent on platform

Source 3: Health System
├─ Nurse visits (frequency, reason)
├─ Chronic condition flags
├─ Vaccination status
├─ Mental health referrals

Source 4: Discipline System
├─ Incident reports (counts by type)
├─ Suspension days
├─ Behavior improvement plans
├─ Restorative practices participation

INTEGRATION CHALLENGES & SOLUTIONS:

Challenge 1: Different update frequencies
├─ SIS: Updated daily (attendance)
├─ LMS: Updated in real-time (assignment submission)
├─ Health: Updated weekly (nurse visits)
├─ Discipline: Updated weekly (incidents)
└─ Solution: Align to common refresh frequency (weekly); backfill recent gaps

Challenge 2: Mismatched student IDs
├─ Problem: Student may have different ID in health vs. SIS
├─ Solution: Manual reconciliation + fuzzy matching (name + DOB)
├─ Validation: Compare record counts before/after merge

Challenge 3: Missing data across sources
├─ Example: Not all students visit nurse, so most records are missing
├─ Solution: Code missing as "no visit" (not same as absence)
└─ Alternative: Model separately (visits vs. non-visits)

Challenge 4: Temporal misalignment
├─ Example: Attendance measured by school day, health by calendar day
└─ Solution: Convert to common time unit (week) for aggregation
```

### 4.3 Risk Dimensions & Feature Groups

```
ACADEMIC RISK DIMENSION

Features:
├─ GPA (0–4.0 scale)
├─ Trend in GPA (improving vs. declining)
├─ Course completion rate (% of courses completed)
├─ Assignment submission rate (% of assignments submitted)
├─ Days with zero engagement (not logged into LMS)
├─ Failed courses in current period
└─ Prerequisite failures (early indicator for next courses)

Rationale:
├─ GPA baseline shows academic preparation level
├─ GPA trend shows whether improving or declining (velocity matters)
├─ Engagement patterns show active or passive student
├─ Assignment submission better than just logins (action-based)
└─ Zero engagement days signal disconnection

Model: Logistic Regression
└─ Why simpler: Academic risk is relatively linear
    (GPA + engagement clearly predict performance)

ATTENDANCE RISK DIMENSION

Features:
├─ Percent days absent (calculated earlier as separate model)
├─ Absence trend (accelerating vs. stable)
├─ Tardies per month
├─ Patterns (e.g., always absent on Mondays)
└─ Known barriers (transportation, health, family)

Rationale:
├─ Absence rate is direct indicator
├─ Absence trend shows whether improving/worsening
├─ Tardies sometimes precede absences (early warning)
├─ Patterns help diagnose root cause
└─ Barriers inform intervention type (not just flagging)

Model: Decision Tree
└─ Why: Interpretable; educators can understand decision logic
         Good at capturing threshold effects (>15% absence = high risk)

HEALTH & WELL-BEING RISK DIMENSION

Features:
├─ Nurse visits (frequency)
├─ Mental health referral flags
├─ Chronic condition flags
├─ Behavioral incidents (count, trend)
├─ Suspensions (in/out of school)
├─ Documented home situation (if available: housing, food insecurity)
└─ Protective factors (sports, clubs, mentoring)

Rationale:
├─ Nurse visits indicate health/wellness concerns
├─ Behavior incidents can signal wellbeing issues
├─ Suspensions are crisis points
├─ Protective factors (sports, clubs) are resilience indicators
└─ Known home stressors (housing) are predictive

Model: Random Forest
└─ Why: Captures complex interactions among health factors
         Can weight protective factors against risk factors

SOCIAL & EQUITY RISK DIMENSION

Features:
├─ First-generation college status (if available)
├─ Socioeconomic status (free/reduced lunch eligibility)
├─ Race/ethnicity (for identifying equity gaps, not as direct risk)
├─ English learner status + English proficiency
├─ Special education status
├─ Foster care / homelessness flags
├─ Home language (non-English speaker)
└─ Transportation barriers (identified)

IMPORTANT: These are context/equity features, not predictive features
├─ Use to: Identify which students need more support
├─ NOT use to: Discriminate or lower expectations
├─ Example: ELL status ≠ at-risk; but barriers for ELL are real
└─ Application: ELL students get academic support in native language

Model Application: Stratified Analysis
├─ Don't predict "at-risk" differently by demographics
├─ DO ensure interventions account for specific barriers
└─ Example: Transportation barrier → arrange bus pass (not tutoring)
```

### 4.4 Composite Well-Being Score Methodology

```
APPROACH: Multi-Dimensional Risk Profile (Not single score)

Stage 1: Normalize each dimension to 0–100 scale
├─ Academic Risk Score: 0 (safe) to 100 (high risk)
├─ Attendance Risk Score: 0 (safe) to 100 (high risk)
├─ Health Risk Score: 0 (safe) to 100 (high risk)
├─ Social/Equity Risk Score: 0 (barriers present) to 100 (many barriers)

Stage 2: Composite score = Weighted average
├─ Default weights: Each dimension = 25%
├─ Can be adjusted by district (e.g., attendance = 40% if priority)
└─ Formula: (0.25×Academic + 0.25×Attendance + 0.25×Health + 0.25×Social)

Stage 3: Generate risk profile
├─ Overall risk: Low (<30), Medium (30–70), High (>70)
├─ Dimension breakdown: Which area needs attention?
└─ Recommendation: Intervention type (tutoring vs. counseling vs. logistics)

Example:
Student A:
├─ Academic: 35 (some struggles)
├─ Attendance: 15 (good attendance)
├─ Health: 20 (no red flags)
├─ Social: 45 (some barriers)
├─ Overall: 29 (Low risk) — Monitor but not urgent

Student B:
├─ Academic: 75 (failing courses)
├─ Attendance: 85 (chronically absent)
├─ Health: 90 (multiple incidents)
├─ Social: 70 (many barriers)
├─ Overall: 80 (High risk) — Immediate intervention needed
└─ Recommendations: Academic tutoring + counseling + transportation + health referral

Validation:
├─ Do flagged students actually need support? (educator feedback)
├─ Are high-risk students caught before dropout? (outcome tracking)
├─ Does intervention reduce risk next period? (effectiveness evaluation)
```

---

## Part 5: Digital Equity Assessment

**Use Case:** Measure connectivity, device access, and digital engagement disparities

### 5.1 Analytical Approach

```
THREE TYPES OF DIGITAL EQUITY ANALYSIS:

Type 1: INFRASTRUCTURE EQUITY
├─ Question: "Which students lack reliable internet?"
├─ Data: Network speed tests, device detection, access logs
├─ Method: Descriptive statistics (% by school/neighborhood)
├─ Output: Maps showing low-access areas
└─ Action: Target broadband expansion, device distribution

Type 2: ENGAGEMENT EQUITY
├─ Question: "Which students are digitally disengaged?"
├─ Data: LMS engagement patterns, login frequency, content access
├─ Method: Comparison across demographics
├─ Output: Difference analysis (are some groups engaging less?)
└─ Action: Targeted digital literacy support

Type 3: OPPORTUNITY GAP EQUITY
├─ Question: "Do students with tech access perform better?"
├─ Data: Device access + academic outcomes
├─ Method: Causal inference (controlling for confounders)
├─ Output: Evidence of tech-outcome relationship
└─ Action: Prioritize device distribution as intervention
```

### 5.2 Infrastructure Equity Metrics

```
NETWORK QUALITY MEASUREMENTS

Data Source: Network speed tests (if available)
Metrics:
├─ Download speed (Mbps) — target >10 Mbps for video
├─ Upload speed (Mbps) — target >5 Mbps for collaboration
├─ Latency (ms) — target <50 ms
├─ Jitter (variance) — target <10 ms variance
├─ Packet loss (%) — target 0%

Aggregation by student home address:
├─ Geocode student addresses (with privacy protection)
├─ Run speed test from address (or estimate from ISP data)
├─ Identify "digital deserts" (areas with <10 Mbps)
└─ Measure: % of students in each quality tier

Device Access Measurement:
├─ LMS logs show device type (mobile, tablet, laptop, Chromebook)
├─ Frequency analysis: % of logins from each device
├─ If always mobile-only → likely no home computer
├─ If zero logins from home IP → may use school devices only
└─ Indicator: Days with zero device access

Statistical Test:
├─ Chi-square test: Is device access independent of zip code?
├─ If significant: Digital divide exists by neighborhood
└─ Calculate effect size (Cramér's V) to quantify disparity

VALIDATION:
└─ Survey 50 families: "Do you have home internet?"
   └─ Sensitivity/specificity of inference model
   └─ Adjust if inference method is inaccurate
```

### 5.3 Engagement Equity Analysis

```
COMPARATIVE ENGAGEMENT METRICS

Measure engagement separately for:
├─ Students with device access (home computer/tablet)
├─ Students with device barriers (mobile-only or school-only)
├─ Different neighborhoods (using address geocoding)
├─ Different demographic groups

Engagement indicators:
├─ Days with any LMS login: % of school days accessed
├─ Assignments submitted: % of assignments turned in
├─ Collaborative activity: # of forum posts / collaborations
├─ Resource access: # of videos watched, pages viewed
└─ Persistence: # of sessions > 30 minutes

Analysis:
├─ Descriptive stats (mean, median, 5th/95th percentile by group)
├─ Statistical test: T-test or Mann-Whitney U (engagement difference)
├─ Effect size: Cohen's d (how big is the difference?)
└─ Interpretation: "Students without home internet login 40% fewer days"

FAIRNESS CHECK:
├─ Compare engagement GIVEN equal device access
├─ If even with access, some groups engage less → pedagogical issue
├─ If disparities disappear with access → infrastructure is key barrier
└─ Helps target interventions (device access vs. digital literacy training)
```

### 5.4 Causal Inference: Does Tech Access Improve Outcomes?

```
CHALLENGE: Correlation vs. Causation
────────────────────────────────────
Observation: Students with home internet have higher GPA
Question: Does internet access CAUSE better grades, or do higher-SES students
          have both internet AND resources for success?

SOLUTION: Causal inference (Difference-in-Differences or matching)

Method 1: PROPENSITY SCORE MATCHING
──────────────────────────────────

Step 1: Identify confounders
├─ Factors that affect both tech access AND grades:
│  ├─ Socioeconomic status (SES)
│  ├─ Parent education level
│  ├─ Student prior achievement
│  └─ Special education status
└─ Data: Use SIS, demographics, prior year grades

Step 2: Build propensity score model
├─ Predict probability of having tech access (logistic regression)
├─ Based only on confounders, not outcome
└─ Output: Score 0–1 for each student

Step 3: Match students
├─ For each student WITH tech access
├─ Find similar student WITHOUT tech access (matching on propensity score)
├─ Now two groups are balanced on confounders
└─ Only difference remaining is tech access

Step 4: Compare outcomes
├─ Treatment group: With tech access
├─ Control group: Matched students without tech
├─ Outcome: Grade improvement (post vs. pre)
├─ Calculate: Average Treatment Effect (ATE)
└─ Result: "Students who gained home internet improved by X GPA points"

VALIDATION:
├─ Covariate balance: Are matched groups actually similar? (t-test)
├─ Sensitivity analysis: If we remove 10% of matching → does conclusion hold?
├─ Robustness: Use multiple matching algorithms (1:1, 1:many, kernel) → similar result?
└─ If all robust → can report causal claim

Method 2: REGRESSION DISCONTINUITY (if applicable)
──────────────────────────────────────────────────

Scenario: District provided devices to students below bandwidth threshold
├─ Before: Students with <5 Mbps had no access
├─ After: All students given hotspot if <5 Mbps
└─ Can measure impact around the "discontinuity"

Analysis:
├─ Compare grades before/after threshold
├─ Control for confounders (grade level, SES)
├─ Estimate causal effect of device access
└─ Higher causal confidence than simple comparison

INTERPRETATION:
├─ If device access causes +0.2 GPA improvement
├─ Then device distribution is evidence-based intervention
├─ Can calculate: Cost per GPA point improvement
└─ Justify investment: "$500/device × impact = $X per 0.1 GPA gain"
```

---

## Part 6: Model Monitoring & Retraining

### 6.1 Drift Detection

```
Two types of drift to monitor:

CONCEPT DRIFT: Model assumptions change
├─ Example: What caused absence 5 years ago differs today
├─ Detection: Model performance drops (accuracy falls >5%)
├─ Action: Retrain on recent data
├─ Schedule: Monthly performance check

DATA DRIFT: Feature distributions change
├─ Example: LMS platform changes how it logs engagement
├─ Detection: Feature distributions shift (Kolmogorov-Smirnov test)
├─ Action: Retrain if >2σ shift
├─ Schedule: Weekly monitoring of feature distributions

IMPLEMENTATION:
├─ Baseline: Model accuracy = 85%
├─ Monthly: Score all students, calculate new accuracy
├─ If accuracy < 80% (5% drop): Flag for investigation
├─ If confirmed drift: Retrain on past 12 months data
└─ Document: What changed? (new LMS features, new school, etc.)
```

### 6.2 Retraining Schedule

```
RECOMMENDED RETRAINING FREQUENCY:

Chronic Absenteeism Model:
├─ Major retrain: Annually (before each new school year)
├─ Minor retrain: Quarterly (adapt to seasonal changes)
└─ Rationale: Absence patterns shift with season (winter breaks, spring events)

Student Well-Being Model:
├─ Major retrain: Annually
├─ Minor retrain: Quarterly
└─ Rationale: Student populations change (seniors graduate)

Digital Equity Model:
├─ Major retrain: Annually
├─ Minor retrain: Semi-annually
└─ Rationale: Infrastructure changes gradually; less drift risk

RETRAINING PROCEDURE:
├─ Step 1: Gather data from past 12 months
├─ Step 2: Re-validate data quality (same Tier 1–4 checks)
├─ Step 3: Retrain model (same algorithm, hyperparameters)
├─ Step 4: Validate on new holdout set
├─ Step 5: Compare new model to previous (5% improvement threshold)
├─ Step 6: If approved, deploy; document changes
└─ Step 7: Monitor performance of new model

DOCUMENTATION:
├─ Version control (Git): Track model code, training date, performance
├─ Change log: What data changed? What drove improvement?
├─ Comparison: Old model accuracy vs. new model accuracy
└─ Approval: Who approved deployment? Why?
```

---

## Part 7: Reproducibility & Audit Trail

### 7.1 Code-Based Analysis (100% Reproducible)

```
All analyses in code (Python + SQL), version controlled:

Repository structure:
├── /01_ingestion/
│   ├── attendance_ingest.py (load SIS data)
│   ├── lms_ingest.py (load LMS data)
│   └── config.yaml (data source credentials, not in Git)
├── /02_validation/
│   ├── data_quality_tests.sql (dbt tests)
│   ├── outlier_detection.py
│   └── validation_report.py
├── /03_features/
│   ├── attendance_features.sql
│   ├── engagement_features.sql
│   └── feature_engineering.py
├── /04_modeling/
│   ├── chronic_absenteeism_model.py
│   ├── well_being_model.py
│   ├── hyperparameter_tuning.py
│   └── fairness_testing.py
├── /05_evaluation/
│   ├── model_performance.py
│   ├── cross_validation.py
│   └── fairness_report.py
└── /06_deployment/
    ├── model_registry.py (log model versions)
    ├── drift_monitoring.py
    └── retraining_pipeline.py

REPRODUCIBILITY GUARANTEES:

Random seed fixed:
├── Python: np.random.seed(42)
├── scikit-learn: random_state=42
├── XGBoost: random_state=42
└─ Purpose: Same code = same results, always

All data transformations in code:
├── No manual Excel steps
├── No undocumented transformations
├── Every feature derivation is auditable
└─ Purpose: Peer can review exact logic

Version control (Git):
├── Tag each model version: v1.0.0, v1.1.0, etc.
├── Commit message explains: "Retrained on 2024 data; accuracy improved 3%"
├── Can revert to any past version if needed
└─ Purpose: Full audit trail of what changed when

Documentation:
├── README explaining: Purpose, inputs, outputs, assumptions
├── Docstrings on every function
├── Jupyter notebooks showing EDA + rationale
└─ Purpose: Colleagues can understand without asking
```

### 7.2 Audit Protocol for External Review

```
PROTOCOL FOR EXTERNAL REVIEWER:

Week 1: Access & Understand
├─ Clone Git repository
├─ Review README and architecture docs
├─ Understand data sources and definitions
└─ Question: "Do the stated goals match the code?"

Week 2: Data Validation
├─ Run data quality checks (dbt tests)
├─ Inspect Tier 1–4 validation results
├─ Review missing data handling
└─ Question: "Is the data clean? Any red flags?"

Week 3: Feature Engineering
├─ Review feature definitions (SQL + Python code)
├─ Understand feature rationale (why each feature?)
├─ Check for data leakage (using future data? → red flag!)
└─ Question: "Are features appropriate for the problem?"

Week 4: Modeling
├─ Review model selection justification
├─ Examine hyperparameter choices
├─ Check cross-validation setup
└─ Question: "Is the model appropriate? Well-tuned?"

Week 5: Fairness & Bias
├─ Review fairness test code and results
├─ Check for demographic disparities
├─ Validate remediation actions taken
└─ Question: "Is the model fair? Any bias?"

Week 6: Validation & Generalization
├─ Review holdout test results
├─ Check if performance generalizes
├─ Examine residuals (prediction errors)
└─ Question: "Does model perform well on new data?"

Week 7: Documentation & Conclusions
├─ Review model assumptions and limitations
├─ Check against original problem statement
├─ Verify all claims in executive summary
└─ Question: "Are conclusions justified?"

REVIEWER OUTPUT:
├─ Approval memo: "Model is valid for deployment"
├─ OR Issues list: "Address X, Y, Z before deployment"
├─ OR Rejection: "Fundamental problems; start over"
└─ Publicly shared (transparency)
```

---

## Part 8: Limitations & Honest Caveats

### 8.1 What These Models CAN'T Do

```
❌ CANNOT: Predict individual student outcomes with certainty
   └─ Can only: Identify risk factors and flag for human review
   └─ Why: Education is complex; many unmeasured factors
   └─ Risk: Over-relying on model recommendations

❌ CANNOT: Work without good data
   └─ Can only: Work well if SIS, LMS, etc. are accurately maintained
   └─ Why: Garbage in, garbage out
   └─ Risk: If data quality poor, model quality poor

❌ CANNOT: Replace teacher judgment
   └─ Can only: Augment teacher knowledge with data
   └─ Why: Teachers know context models don't
   └─ Risk: Educators ignoring model and relying entirely on it

❌ CANNOT: Identify students who will succeed without support
   └─ Can only: Identify those at higher risk than peers
   └─ Why: Assumes support is available and accepted
   └─ Risk: Flagged students not getting intervention

❌ CANNOT: Solve systemic inequities
   └─ Can only: Make inequities visible so they can be addressed
   └─ Why: Model can identify gaps, but can't close them
   └─ Risk: Identifying problem without resources to fix it

❌ CANNOT: Account for unmeasured factors
   └─ Can only: Work with data available
   └─ Why: May miss important context (family crisis, new meds, etc.)
   └─ Risk: False negatives (miss students actually needing help)
```

### 8.2 Key Assumptions & When They Fail

```
Assumption 1: Historical data is representative
├─ Example: Model trained on pre-pandemic data; used during lockdown
├─ Problem: Absence patterns completely different online
├─ Solution: Retrain on 2020–2021 data; don't use pre-pandemic model
└─ Lesson: Monitor for concept drift; retrain when patterns change

Assumption 2: Data is correctly labeled
├─ Example: "Absent" coded inconsistently across schools
├─ Problem: Some mark unexcused absence, others don't specify
├─ Solution: Data quality audit; standardize definitions
└─ Lesson: Invest in clean data before modeling

Assumption 3: Features are stable
├─ Example: LMS changes how it logs engagement
├─ Problem: Feature distributions shift; model performance drops
├─ Solution: Retrain on new LMS data; monitor for drift
└─ Lesson: Document data source changes; plan for retraining

Assumption 4: Relationships don't change
├─ Example: Engagement used to predict attendance; now doesn't
├─ Problem: Model trained on old relationship
├─ Solution: Investigate what changed (online learning?); retrain
└─ Lesson: Periodically validate that features still predictive

Assumption 5: Students are independent
├─ Example: If one student leaves school, affects peer group composition
├─ Problem: Clustered data (students within school); not all independent
├─ Solution: Cluster standard errors; account for school effects
└─ Lesson: Use hierarchical/mixed models for education data
```

### 8.3 Recommendations for Use

```
✅ DO:
├─ Use flagged students as starting point for conversations
├─ Let educators provide context (family situation, recent trauma)
├─ Combine data insights with student & family voice
├─ Treat predictions as hypotheses, not certainties
├─ Monitor outcomes (did intervention help?)
├─ Retrain model regularly (annually minimum)
├─ Publish fairness results (transparency)
└─ Respect student privacy (use pseudonymization)

❌ DON'T:
├─ Fully automate decisions (require human review)
├─ Use model alone (integrate with other information)
├─ Expect 100% accuracy (expect ~80–85% on education outcomes)
├─ Ignore fairness concerns (test for bias)
├─ Deploy without stakeholder input (educators, families)
├─ Forget about privacy (even aggregate data can be sensitive)
├─ Assume model stays accurate (monitor for drift)
└─ Apply model beyond its intended scope (a Chronic Absenteeism 
   model is not a dropout predictor)
```

---

## Part 9: Comparison to Alternative Approaches

### 9.1 Why Not Simple Rules?

```
ALTERNATIVE 1: Rule-Based System
Example: "If absence >15%, flag as at-risk"

ADVANTAGES:
├─ Fully interpretable (easy to explain)
├─ No model training needed
├─ Deployment instant
└─ No fairness concerns (same rule for all)

DISADVANTAGES:
├─ MISSES early warning (waits until >15% absence)
├─ IGNORES context (e.g., excused vs. unexcused)
├─ NO predictive power for new students (no baseline)
├─ CRUDE (can't weight engagement signal)
└─ Example: Student A: 14% absence + zero engagement = high risk
            Student B: 15% absence + high engagement = lower risk
            Rule-based flags only Student B (wrong!)

COMPARISON:
Rule-Based:       Catch 60% of at-risk students (low sensitivity)
ML Model:         Catch 85% of at-risk students (higher sensitivity)
                  Fewer false alarms (higher precision)

RECOMMENDATION: Use ML model, explain predictions using rule-like features
└─ Get accuracy of ML + interpretability of rules
```

### 9.2 Why Not Simpler Algorithms?

```
ALTERNATIVE 2: Logistic Regression
Simple, linear, fully interpretable

ADVANTAGES:
├─ Coefficients directly interpretable ("each 1% absence increases risk by X%")
├─ Fast to train and explain
├─ Standard statistical theory (confidence intervals, significance tests)
└─ Good baseline to compare against

DISADVANTAGES:
├─ Assumes linear relationships (absence + engagement is non-linear)
├─ Misses interaction effects (e.g., "engagement matters more if attendance low")
├─ Can't capture complex patterns
└─ Performance: Typical accuracy 78% vs. XGBoost 85%

RECOMMENDATION: Use XGBoost as primary, logistic regression as validation baseline
└─ Confirm XGBoost results with simpler model
└─ If logistic regression gives same top risk factors, confidence is higher
```

### 9.3 Why Not Simpler Data?

```
ALTERNATIVE 3: Attendance-Only Prediction
Use only SIS attendance data; ignore engagement, barriers, demographics

ADVANTAGES:
├─ Simple data collection (only SIS)
├─ Fewer privacy concerns (less sensitive data)
├─ Easier to explain ("just based on absences")
└─ Clear intervention (address barriers to attendance)

DISADVANTAGES:
├─ Missing key signal: Engagement (online student might have zero absences)
├─ Missing context: Why absent? (health vs. choice vs. barriers)
├─ Lower accuracy: ~75% vs. ~85% with full data
└─ Equity concern: Some barriers only visible in engagement (no device access)

COMPARISON:
Attendance-Only:    Catch 72% of at-risk
Multi-Source:       Catch 85% of at-risk
                    Better equity: Identifies tech access barriers

RECOMMENDATION: Use multi-source, but prioritize attendance as primary signal
└─ Attendance most predictive, but insufficient alone
└─ Engagement + barriers provide crucial context
```

---

## Part 10: Validation & External Peer Review

### 10.1 Peer Review Checklist

For someone reviewing OEA's analytical approach:

```
METHODOLOGY REVIEW:

☐ Data Quality
  ├─ Are validation rules appropriate?
  ├─ Is missing data handled transparently?
  ├─ Are outliers identified and documented?
  └─ Are data quality metrics published?

☐ Feature Engineering
  ├─ Is feature rationale documented?
  ├─ Are features derived correctly?
  ├─ Is there any data leakage? (using future info to predict past)
  └─ Are features stable (won't change meaning)?

☐ Model Selection
  ├─ Is algorithm choice justified?
  ├─ Are alternatives considered?
  ├─ Are hyperparameters tuned appropriately?
  └─ Is model complexity justified by performance gain?

☐ Validation
  ├─ Is cross-validation setup appropriate?
  ├─ Is holdout test set truly held out?
  ├─ Are performance metrics reported completely?
  └─ Is performance on different student groups similar?

☐ Fairness
  ├─ Are fairness tests documented?
  ├─ Are disparities identified and remediated?
  ├─ Are limitations transparent?
  └─ Is fairness testing replicable?

☐ Reproducibility
  ├─ Is code version controlled?
  ├─ Are random seeds fixed?
  ├─ Can someone run your code and get same results?
  └─ Is documentation sufficient for replication?

☐ Limitations
  ├─ Are assumptions stated?
  ├─ Are limitations acknowledged?
  ├─ Are recommendations for use clear?
  └─ Is scope of validity defined?

APPROVAL: ☐ Approve   ☐ Conditional (address issues)   ☐ Reject
Comments: _________________________________________________
```

### 10.2 Where to Find Technical Details

```
For each OEA package, available documentation:

/oss_framework/packages/[package_name]/
├── notebooks/
│   ├── 01_EDA.ipynb                         (Exploratory analysis)
│   ├── 02_FeatureEngineering.ipynb          (Feature rationale + code)
│   ├── 03_ModelTraining.ipynb               (Training process, hyperparameters)
│   ├── 04_ModelEvaluation.ipynb             (Performance, fairness, cross-validation)
│   └── 05_Deployment.ipynb                  (How to score new data)
├── src/
│   ├── feature_engineering.py               (Reproducible feature code)
│   ├── model_pipeline.py                    (Model training code)
│   ├── fairness_assessment.py               (Fairness testing code)
│   └── model_monitoring.py                  (Drift detection code)
├── data/
│   └── sample_[package]_data.parquet        (Synthetic data for testing)
├── README.md                                (Overview, use cases, limitations)
└── technical_specification.md               (This document, for that package)

REQUEST FOR PEER REVIEW:
├─ Email: [OEA contact]
├─ Subject: "Peer Review of [Package] Analytics"
├─ What you want reviewed: Methodology, fairness, statistical validity
└─ Timeline: Specify (e.g., "Need feedback by [date]")
```

---

## Conclusion: Transparent, Reviewable Analytics

OEA is designed for **peer review and transparency**:

✅ **Methods are published** - Not hidden in proprietary models  
✅ **Code is available** - Not obscured or compiled  
✅ **Assumptions are documented** - Not assumed and invisible  
✅ **Limitations are stated** - Not oversold  
✅ **Fairness is tested** - Not assumed to be fair  
✅ **Results are reproducible** - Not dependent on person/timing  
✅ **External review is welcomed** - Not defensive about methodology  

**This technical breakdown exists so data experts can:**
- Understand exactly what OEA models do
- Evaluate whether methods are appropriate
- Identify gaps or concerns
- Propose improvements
- Replicate findings independently
- Trust the analyses (or propose alternatives)

**Questions? Concerns?** We welcome peer review and are committed to addressing valid technical critiques.

---

**Document Version:** 1.0  
**Last Updated:** January 26, 2026  
**Audience:** Data scientists, statisticians, analytics professionals, audit teams  
**For Questions:** Contact [OEA Data Leadership]

