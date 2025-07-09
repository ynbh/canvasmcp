
import { tool } from "ai";
import { listGradeableStudentsDataSchema } from "./aitm.schema.ts";
import { listGradeableStudents, ListGradeableStudentsData } from "..";

export default tool({
  description: `
  List gradeable students
A paginated list of students eligible to submit the assignment. The caller
must have permission to view grades.

Section-limited instructors will only see students in their
own sections.

returns [UserDisplay]
    `,
  parameters: listGradeableStudentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGradeableStudentsData, "url"> ) => {
    try {
      const { data } = await listGradeableStudents(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    