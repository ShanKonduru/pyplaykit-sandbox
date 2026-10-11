-- ============================================================================
-- SOURCE database seed  (legacy schema -- abbreviated column names)
-- ============================================================================
-- Runs automatically on first container start. Creates two tables and loads
-- thousands of rows using deterministic formulas so that, by default, SRC and
-- TGT hold identical business data. The TGT seed then introduces a handful of
-- deliberate, *visible* differences (see tgt_init.sql).
--
--   department : 50 rows
--   employee   : 5000 rows
--
-- Columns ending in a metadata purpose (created_ts, row_version) are meant to
-- be ignored during comparison -- they legitimately differ between systems.
-- ============================================================================

CREATE TABLE department (
    dept_id     INTEGER PRIMARY KEY,
    dept_nm     TEXT        NOT NULL,
    dept_loc    TEXT        NOT NULL,
    row_version INTEGER     NOT NULL DEFAULT 1        -- metadata: ignore in compare
);

CREATE TABLE employee (
    emp_id       INTEGER PRIMARY KEY,
    emp_nm       TEXT        NOT NULL,
    emp_dept_id  INTEGER     NOT NULL REFERENCES department(dept_id),
    emp_sal      NUMERIC(10,2) NOT NULL,
    emp_email    TEXT        NOT NULL,
    created_ts   TIMESTAMP   NOT NULL DEFAULT now()   -- metadata: ignore in compare
);

-- 50 departments -------------------------------------------------------------
INSERT INTO department (dept_id, dept_nm, dept_loc, row_version)
SELECT
    d,
    'Department_' || d,
    'City_' || ((d % 10) + 1),
    1
FROM generate_series(1, 50) AS d;

-- 5000 employees -------------------------------------------------------------
INSERT INTO employee (emp_id, emp_nm, emp_dept_id, emp_sal, emp_email, created_ts)
SELECT
    e,
    'Employee_' || e,
    (e % 50) + 1,
    (40000 + (e % 100) * 500)::numeric(10,2),
    'user' || e || '@example.com',
    now()
FROM generate_series(1, 5000) AS e;
