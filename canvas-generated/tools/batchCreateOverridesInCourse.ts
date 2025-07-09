
import { tool } from "ai";
import { batchCreateOverridesInCourseDataSchema } from "./aitm.schema.ts";
import { batchCreateOverridesInCourse, BatchCreateOverridesInCourseData } from "..";

export default tool({
  description: `
  Batch create overrides in a course
Creates the specified overrides for each assignment.  Handles
creation in a
transaction, so all records are created or none are.

One of student_ids, group_id, or
course_section_id must be present. At most
one should be present; if multiple are present only the
most specific
(student_ids first, then group_id, then course_section_id) is used and any
others are
ignored.

Errors are reported in an errors attribute, an array of errors corresponding
to inputs.
Global errors will be reported as a single element errors array
    `,
  parameters: batchCreateOverridesInCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<BatchCreateOverridesInCourseData, "url"> ) => {
    try {
      const { data } = await batchCreateOverridesInCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    