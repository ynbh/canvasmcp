
import { tool } from "ai";
import { getDepartmentLevelGradeDataCurrentDataSchema } from "./aitm.schema.ts";
import { getDepartmentLevelGradeDataCurrent, GetDepartmentLevelGradeDataCurrentData } from "..";

export default tool({
  description: `
  Get department-level grade data
Returns the distribution of grades for students in courses in
the
department.  Each data point is one student's current grade in one course;
if a student is in
multiple courses, he contributes one value per course,
but if he's enrolled multiple times in the
same course (e.g. a lecture
section and a lab section), he only constributes on value for that
course.

Grades are binned to the nearest integer score; anomalous grades outside
the 0 to 100 range
are ignored. The raw counts are returned, not yet
normalized by the total count.

Shares the same
variations on endpoint as the participation data.
    `,
  parameters: getDepartmentLevelGradeDataCurrentDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetDepartmentLevelGradeDataCurrentData, "url"> ) => {
    try {
      const { data } = await getDepartmentLevelGradeDataCurrent(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    