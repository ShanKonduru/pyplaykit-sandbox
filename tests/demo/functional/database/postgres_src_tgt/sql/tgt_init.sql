-- ============================================================================
-- TARGET database seed  (migrated schema -- full column names)
-- ============================================================================
-- Same business data as the SOURCE, but:
--   * column names are the "new system" full names (employee_id, name, ...)
--   * metadata columns differ on purpose (row_version bumped, created_ts later)
--   * a handful of DELIBERATE, VISIBLE data differences are injected so the
--     comparison report shows real mismatches / missing / extra rows.
--
--   department : 50 rows
--   employee   : 5000 rows (with the differences below)
--
-- Injected differences (what the report should catch):
--   employee 100  -> salary changed          (VALUE_MISMATCH: salary)
--   employee 250  -> name changed            (VALUE_MISMATCH: name)
--   employee 375  -> email changed           (VALUE_MISMATCH: email)
--   employee 500  -> salary + name changed   (VALUE_MISMATCH: 2 fields)
--   employee 4999 -> DELETED in target       (SOURCE_ONLY)
--   employee 5001 -> EXTRA row in target      (TARGET_ONLY)
--   department 7  -> location changed        (VALUE_MISMATCH: location)
-- ============================================================================

CREATE TABLE department (
    department_id INTEGER PRIMARY KEY,
    name          TEXT        NOT NULL,
    location      TEXT        NOT NULL,
    row_version   INTEGER     NOT NULL DEFAULT 2       -- metadata: differs, ignore
);

CREATE TABLE employee (
    employee_id  INTEGER PRIMARY KEY,
    name         TEXT        NOT NULL,
    department_id INTEGER    NOT NULL REFERENCES department(department_id),
    salary       NUMERIC(10,2) NOT NULL,
    email        TEXT        NOT NULL,
    created_ts   TIMESTAMP   NOT NULL DEFAULT now()    -- metadata: differs, ignore
);

-- 50 departments (identical data, bumped row_version) ------------------------
INSERT INTO department (department_id, name, location, row_version)
SELECT
    d,
    'Department_' || d,
    'City_' || ((d % 10) + 1),
    2
FROM generate_series(1, 50) AS d;

-- 5000 employees (identical formula -> same data as source) ------------------
INSERT INTO employee (employee_id, name, department_id, salary, email, created_ts)
SELECT
    e,
    'Employee_' || e,
    (e % 50) + 1,
    (40000 + (e % 100) * 500)::numeric(10,2),
    'user' || e || '@example.com',
    now()
FROM generate_series(1, 5000) AS e;

-- Inject deliberate, visible differences ------------------------------------

-- department 7: location changed
UPDATE department SET location = 'Relocated_City' WHERE department_id = 7;

-- employee 100: salary changed
UPDATE employee SET salary = 99999.99 WHERE employee_id = 100;

-- employee 250: name changed
UPDATE employee SET name = 'Renamed_Employee_250' WHERE employee_id = 250;

-- employee 375: email changed
UPDATE employee SET email = 'changed375@example.com' WHERE employee_id = 375;

-- employee 500: two fields changed
UPDATE employee SET salary = 123456.00, name = 'Changed_Employee_500' WHERE employee_id = 500;

-- employee 4999: exists in source, missing here (source-only)
DELETE FROM employee WHERE employee_id = 4999;

-- employee 5001: extra row not present in source (target-only)
INSERT INTO employee (employee_id, name, department_id, salary, email)
VALUES (5001, 'Extra_Employee_5001', 1, 55000.00, 'extra5001@example.com');
