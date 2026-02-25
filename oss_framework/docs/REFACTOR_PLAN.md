# Refactoring Plan: Open Source OpenEduAnalytics (OEA) for Small School Districts

## Executive Summary

**Target Audience**: Small School District (6 schools, ~1,700 students).
**Goal**: Migrate from Azure Synapse/Data Lake to a lightweight, open-source stack (DuckDB "Modern Data Stack in a Box").
**Constraint**: Minimal IT overhead, zero software licensing costs, single-server deployment.

This plan outlines the refactoring of the OEA repository to support a "Local-First" architecture that scales to the cloud only if needed. For 1,700 students, the entire data platform can run efficiently on a single standard server (or high-end laptop) using Docker Compose.

---

## 1. Architecture: The "DuckLake" Stack

We will replace the heavy Azure components with lightweight, high-performance open-source alternatives.

| Layer | Current Azure Component | Recommended Open Source Replacement | Rationale for Small District |
|-------|-------------------------|-------------------------------------|------------------------------|
| **Storage** | Azure Data Lake Gen2 (ADLS) | **Local Filesystem + Parquet** | Zero cost, simple backup, high performance for <1TB data. |
| **Compute** | Azure Synapse (Spark) | **DuckDB** | In-process analytical DB. 10-100x faster than Spark for small data. No cluster management. |
| **Ingest** | Synapse Pipelines | **dlt (Data Load Tool)** | Pythonic, schema evolution, handles JSON APIs easily. |
| **Transform** | Synapse Notebooks | **dbt Core (with dbt-duckdb)** | SQL-based transformations, built-in testing, documentation. |
| **Orchestrate**| Synapse Triggers | **Dagster** or **Prefect** | Lightweight orchestration, easy to debug locally. |
| **Visualize** | Power BI | **Metabase** (OSS Docker) | Easy UI for school leaders, runs in Docker, free. |

### Technology Selection Deep Dive

#### DuckDB vs. Alternatives
- **DuckDB**: Chosen for its simplicity and performance. It reads Parquet/Delta files directly without import, perfect for a "query-in-place" lakehouse architecture.
- **PostgreSQL**: Considered but rejected. It requires data import (ETL) and is OLTP-oriented, not optimized for analytical queries on large datasets.
- **SQLite**: Rejected. Not designed for concurrent analytical workloads and lacks Parquet support.

#### dbt-duckdb vs. Alternatives
- **dbt-duckdb**: Provides the full power of dbt (testing, documentation, DAG) with DuckDB's performance. Ideal for SQL-first transformations.
- **Pandas/Polars**: Rejected for complex transformations. While powerful for data wrangling, they lack the declarative SQL approach, testing framework, and documentation generation of dbt.

#### dlt vs. Alternatives
- **dlt (Data Load Tool)**: Chosen for its "Python-first" approach and automatic schema handling. It simplifies API ingestion and manages state/incremental loads out-of-the-box.
- **Airflow**: Rejected as overkill for simple ingestion. It's a full workflow orchestrator, not just an ingestion tool.
- **Custom Scripts**: Rejected due to the need to reinvent state management, schema evolution, and error handling.

#### Metabase vs. Alternatives
- **Metabase**: Chosen for its ease of use and quick setup. School administrators can create dashboards without technical expertise.
- **Apache Superset**: More powerful but has a steeper learning curve. Overkill for basic district dashboards.
- **Grafana**: Rejected. Primarily for metrics/monitoring, not business intelligence dashboards.

### Diagram
```mermaid
graph LR
    Sources[SIS / LMS / CSV] --> Ingest[Python + dlt]
    Ingest --> Raw[Raw Parquet (Stage 1)]
    Raw --> dbt[dbt + DuckDB]
    dbt --> Refined[Refined Tables (Stage 2/3)]
    Refined --> BI[Metabase / Superset]
    Refined --> DuckDB_File[oea.duckdb]
```

---

## 2. Refactoring Steps

### Phase 1: Environment & Structure (Weeks 1-2)
*Objective: Create a portable development environment.*

1.  **Clean Repository Structure**:
    *   Create a new root directory `oss_framework/`.
    *   Create `docker-compose.yml` to spin up Metabase, Dagster, and a JupyterLab instance.
    *   Create `requirements.txt` with `duckdb`, `dbt-duckdb`, `dlt`, `pandas`.

2.  **Define Storage Layout (The "Lake")**:
    *   Establish a standard folder structure on the local disk (mimicking ADLS):
        ```text
        data/
          ├── stage1 (raw)
          ├── stage2 (ingested/delta/parquet)
          └── stage3 (refined)
        ```

### Phase 2: Ingestion Replacement (Weeks 3-4)
*Objective: Replace Synapse Pipelines with Python scripts.*

1.  **Port "Land" Pipelines**:
    *   Convert `framework/synapse/pipeline/*_land_*.json` logic to Python scripts using `dlt`.
    *   *Example*: A script to fetch Ed-Fi JSON and save as Parquet to `data/stage1`.
    *   **Pseudonymization**: Implement the OEA hashing logic (from `opensource_assessment.md`) as a standard Python utility function or dbt macro.

2.  **Create Ingestion Framework**:
    *   Build a generic `dlt` pipeline template that can be configured for different data sources (SIS, LMS, etc.).
    *   Implement automatic data type inference and schema validation.
    *   Add support for incremental loads and change data capture (CDC) where applicable.

### Phase 3: Transformation Replacement (Weeks 5-6)
*Objective: Replace Spark Notebooks with dbt models.*

1.  **Configure dbt**:
    *   Initialize a dbt project `oea_dbt`.
    *   Configure `profiles.yml` to point to the local DuckDB file.
    *   Set up dbt packages (dbt_utils, calendar_date) for common transformations.

2.  **Migrate Logic**:
    *   Convert Spark SQL logic from `framework/synapse/notebook/` into dbt SQL models.
    *   *Stage 2*: Clean, deduplicate, and type-cast raw data.
    *   *Stage 3*: Create dimensional models (Students, Attendance, Grades) for reporting.

3.  **Implement Data Quality**:
    *   Add dbt tests for null checks, uniqueness, referential integrity.
    *   Create data quality dashboards in Metabase to monitor pipeline health.
    *   Set up automated alerts for data quality failures.

### Phase 4: Visualization (Week 7)
*Objective: Replace Power BI with Metabase.*

1.  **Setup Metabase**:
    *   Connect Metabase to the `oea.duckdb` file (or expose DuckDB via a lightweight PostgreSQL shim if needed, though native drivers exist).
    *   Recreate key dashboards (Attendance, Digital Activity) from the `hack_assessment.md` requirements.

2.  **Create District Dashboards**:
    *   **Student Overview**: Enrollment, demographics, attendance trends.
    *   **Academic Performance**: Grade distributions, assessment scores, course completion rates.
    *   **Digital Engagement**: LMS usage, online learning patterns, device access.
    *   **Operational Metrics**: Teacher workload, classroom utilization, resource allocation.

3.  **Configure Access Control**:
    *   Set up role-based access (Admin, Principal, Teacher, Staff).
    *   Implement row-level security for sensitive student data.
    *   Create audit logs for dashboard access.

---

## 3. Deployment Guide (Getting Started)

### Prerequisites
*   A machine with 16GB+ RAM (Ubuntu Linux recommended, or Windows with WSL2).
*   Docker & Docker Compose installed.
*   Python 3.10+.

### Setup Command (Draft)
```bash
# 1. Clone Repo
git clone https://github.com/flucido/openedDataEstate.git
cd openedDataEstate/oss_framework

# 2. Start Services (Metabase, Orchestrator)
docker-compose up -d

# 3. Run Ingestion (Example)
python scripts/ingest_sis.py

# 4. Run Transformations
dbt build
```

---

## 4. Key Recommendations for Small Districts

1.  **Avoid Kubernetes**: It adds unnecessary complexity for a single school district. A single "beefy" server is easier to manage and debug.
2.  **Use Parquet**: It is the standard for open-source data lakes. DuckDB reads it natively and incredibly fast.
3.  **dbt is non-negotiable**: It brings software engineering best practices (version control, testing) to your data transformations without complex code.
4.  **Security**: Keep the server inside the district's private network (VPN access only). Use DuckDB's encryption features if data at rest encryption is strictly required by policy, or rely on disk encryption (BitLocker/LUKS).

### Additional Recommendations

5.  **Start Simple**: Don't try to migrate all modules at once. Begin with one critical data source (e.g., student attendance) and expand from there.
6.  **Document Everything**: Create a simple data dictionary and process documentation. School districts often have high staff turnover.
7.  **Plan for Growth**: While starting with a single server, design the architecture to be portable to cloud or larger infrastructure if needed.
8.  **Training Investment**: Allocate time for IT staff to learn the new stack. The learning curve is gentler than Azure but still requires investment.

---

## 5. Task Plan Development

### Phase 1: Detailed Task Planning (Next 2 Weeks)
*Objective: Create comprehensive, actionable task lists for each implementation phase.*

#### 5.1 Environment Setup Tasks
- [ ] Create detailed directory structure specification
- [ ] Define Docker Compose service configurations
- [ ] Specify Python package versions and dependencies
- [ ] Create local development environment setup guide
- [ ] Document data lake folder structure and permissions

#### 5.2 Ingestion Framework Tasks
- [ ] Design generic dlt pipeline template architecture
- [ ] Create configuration schema for different data sources
- [ ] Implement pseudonymization utility functions
- [ ] Define error handling and retry mechanisms
- [ ] Create data validation and quality check framework

#### 5.3 Transformation Framework Tasks
- [ ] Design dbt project structure and naming conventions
- [ ] Create standard dbt macros for common transformations
- [ ] Define data model templates (staging, intermediate, marts)
- [ ] Implement automated testing framework
- [ ] Create documentation generation templates

#### 5.4 Visualization Framework Tasks
- [ ] Define dashboard template specifications
- [ ] Create Metabase configuration and setup guide
- [ ] Design role-based access control framework
- [ ] Specify data model requirements for dashboards
- [ ] Create dashboard development guidelines

### Phase 2: Proof of Concept Tasks (Weeks 3-4)
*Objective: Implement a complete end-to-end example using student attendance data.*

#### 5.5 Sample Implementation Tasks
- [ ] Create sample student attendance data generator
- [ ] Implement dlt ingestion pipeline for attendance data
- [ ] Develop dbt models for attendance analytics
- [ ] Create Metabase dashboard for attendance reporting
- [ ] Document complete workflow and troubleshooting guide

### Phase 3: Migration Planning Tasks (Weeks 5-6)
*Objective: Plan the migration of existing OEA modules to the new architecture.*

#### 5.6 Module Analysis Tasks
- [ ] Inventory all existing OEA modules and dependencies
- [ ] Prioritize modules for migration based on district needs
- [ ] Create migration complexity assessment for each module
- [ ] Define data mapping between old and new architectures
- [ ] Plan parallel operation strategy during transition

#### 5.7 Risk Management Tasks
- [ ] Create detailed risk register for each implementation phase
- [ ] Define rollback procedures for each major component
- [ ] Plan data backup and recovery strategies
- [ ] Create testing and validation procedures
- [ ] Define success criteria and acceptance tests

### Phase 4: Documentation and Training Tasks (Weeks 7-8)
*Objective: Create comprehensive documentation and training materials.*

#### 5.8 Documentation Tasks
- [ ] Write system architecture documentation
- [ ] Create installation and setup guides
- [ ] Develop user manuals for each component
- [ ] Create troubleshooting and FAQ documents
- [ ] Document API specifications and data contracts

#### 5.9 Training Tasks
- [ ] Create training curriculum for IT staff
- [ ] Develop hands-on lab exercises
- [ ] Create video tutorials for common tasks
- [ ] Plan knowledge transfer sessions
- [ ] Create certification and competency assessments

### Phase 5: Implementation Readiness Tasks (Weeks 9-10)
*Objective: Prepare for full implementation with all necessary tools and processes.*

#### 5.10 Tool and Process Tasks
- [ ] Create project management templates and workflows
- [ ] Set up version control and code review processes
- [ ] Define deployment and release procedures
- [ ] Create monitoring and alerting frameworks
- [ ] Establish change management processes

#### 5.11 Quality Assurance Tasks
- [ ] Define coding standards and best practices
- [ ] Create code review checklists
- [ ] Establish automated testing pipelines
- [ ] Define performance benchmarks and testing
- [ ] Create security audit procedures

---

## 6. Implementation Roadmap

### Short-term (Months 2-3)
1.  **Proof of Concept**: Implement end-to-end pipeline for one data source.
2.  **Staff Training**: Conduct hands-on training for IT staff.
3.  **Security Review**: Implement security controls and conduct audit.

### Medium-term (Months 4-6)
1.  **Module Migration**: Port 2-3 additional OEA modules.
2.  **Dashboard Development**: Create initial district dashboards.
3.  **Documentation**: Complete user guides and technical documentation.

### Long-term (Months 7-12)
1.  **Full Migration**: Complete migration of all critical data sources.
2.  **Optimization**: Performance tuning and process improvements.
3.  **Knowledge Transfer**: Train district staff to manage the system independently.

---

## 6. Risk Mitigation

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|-------------------|
| Staff Resistance | Medium | High | Involve staff early, provide comprehensive training, start with simple wins |
| Data Migration Issues | Low | High | Parallel runs, comprehensive testing, rollback procedures |
| Performance Issues | Low | Medium | Proof of concept, benchmarking, hardware sizing |
| Security Breaches | Low | High | Security audit, access controls, encryption |
| Vendor Lock-in (New) | Low | Medium | Use open standards (Parquet, SQL), avoid proprietary features |

---

## 7. Success Metrics

### Technical Metrics
- **Query Performance**: <2 seconds for standard dashboard queries
- **Data Freshness**: <24 hours for most data sources
- **System Uptime**: >99% during business hours
- **Data Quality**: <1% error rate in critical fields

### Business Metrics
- **User Adoption**: >80% of administrators using dashboards weekly
- **Time to Insight**: <5 minutes to answer common questions
- **Cost Savings**: Achieve projected $11,400 annual savings
- **Decision Quality**: Track data-driven decisions and outcomes

---

## 8. Conclusion

This refactoring plan provides a pragmatic path for small school districts to leverage modern data analytics without the complexity and cost of enterprise cloud platforms. The "DuckLake" architecture offers:

- **Simplicity**: Single-server deployment with minimal DevOps overhead
- **Performance**: Fast query response times for district-scale data
- **Flexibility**: Open-source stack that can grow with district needs
- **Cost-Effectiveness**: Zero software licensing costs and minimal infrastructure

By following this plan, a small school district can implement a robust data analytics platform that serves immediate needs while providing a foundation for future growth.

---

## 9. Next Steps for Task Planning

1.  **Approve this detailed task plan.**
2.  Upon approval, this plan will be ready for future implementation.
3.  The detailed task lists and specifications will be created when work resumes.
4.  All templates and frameworks will be developed during the implementation phase.
5.  Success criteria and acceptance tests will be established before each task execution.
