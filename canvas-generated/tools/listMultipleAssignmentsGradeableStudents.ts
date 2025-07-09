
import { tool } from "ai";
import { listMultipleAssignmentsGradeableStudentsDataSchema } from "./aitm.schema.ts";
import { listMultipleAssignmentsGradeableStudents, ListMultipleAssignmentsGradeableStudentsData } from "..";

export default tool({
  description: `
  List multiple assignments gradeable students
A paginated list of students eligible to submit a list
of assignments. The caller must have
permission to view grades for the requested
course.

Section-limited instructors will only see students in their own sections.
    `,
  parameters: listMultipleAssignmentsGradeableStudentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListMultipleAssignmentsGradeableStudentsData, "url"> ) => {
    try {
      const { data } = await listMultipleAssignmentsGradeableStudents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    