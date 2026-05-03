# Excel Data Query Operation Manual

This manual provides a step-by-step guide on how to perform cross-table data queries in Excel using the 5 provided datasets (Enrollments, Students, Supervisors, Sessions, and Courses) without using complex formulas.

---

## 1. Understanding Data Relationships

To perform queries correctly, you must understand how the 5 tables connect to each other:

1. **Enrollments**: Everything starts from the **`enrollments`** table.
2. **Students**: `enrollments` links to **`students`** via the `student_id` field.
3. **Supervisors**: `students` links to **`supervisors`** via the `supervisor_id` field.
4. **Sessions**: `enrollments` links to **`sessions`** via the `session_id` field.
5. **Courses**: `sessions` links to **`courses`** via the `course_id` field.

---

## 2. Setup: Importing and Connecting Data

### Step 1: Import Data correctly

1. Open a **new, blank** Excel workbook (do not build the model directly inside your raw data file to keep it safe).
2. Go to the **Data** tab ➡️ **Get Data** ➡️ **From File** ➡️ **From Excel Workbook**.
3. Locate and select your **`2026_output.xlsx`** file, then click **Import**.
4. In the Navigator window that appears, check the box for **Select multiple items** (usually at the top left).
5. Check the boxes next to all 5 sheets: `enrollments`, `students`, `supervisors`, `sessions`, and `courses`.
6. **CRITICAL**: Do **NOT** click "Load" directly. Click the arrow next to the "Load" button at the bottom and select **Load To...**.
7. Select **Only Create Connection** AND check the box **Add this data to the Data Model**. Click **OK**.

---

## 3. Querying Data using PivotTables

1. In your Excel sheet, go to **Insert** ➡️ **PivotTable** ➡️ **From Data Model**. Click **OK**.
2. The **PivotTable Fields** panel will appear on the right, showing all 5 tables.

> 🌟 **THE GOLDEN RULE** 🌟
> Whenever you perform a query, you **MUST** drag an ID field (like `student_id` or `enrollment_id`) into the **Values** area at the bottom right.
>
> *Why?* Excel only calculates the relationships between tables when it is forced to "count" or "calculate" something. Without a value, filters from one table might not affect the display of another table.

---

## 4. Practical Query Scenarios

### Scenario A: Which students are under a specific supervisor (e.g., SMS)?

1. Expand the `supervisors` table and drag **`full_name`** to the **Filters** area.
2. Expand the `students` table and drag **`full_name`** and **`company`** to the **Rows** area.
3. Drag **`student_id`** from the `students` table to the **Values** area.
4. Now, use the filter at the top of your sheet to select "SMS". The list will instantly update to show only his students.

### Scenario B: How many enrollments are there for each course?

1. Expand the `courses` table and drag **`course_name`** to the **Rows** area.
2. Expand the `enrollments` table and drag **`enrollment_id`** to the **Values** area.
3. Excel will display the total enrollment count for every course.

### Scenario C: List of pending payments by company

1. Expand `enrollments` and drag **`payment_status`** to the **Filters** area. Set the filter to **`PENDING`**.
2. Expand `students` and drag **`company`** to the **Rows** area.
3. Drag **`student_id`** from `students` to the **Values** area.
4. You now have a neat list showing which companies have pending payments and how many.

---

## 5. Troubleshooting

If a filter is not working:

1. Check if you have a field in the **Values** area.
2. Go back to **Data > Data Model > Diagram View** and ensure the lines are connecting the correct matching ID fields.
