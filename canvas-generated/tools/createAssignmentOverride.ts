
import { tool } from "ai";
import { createAssignmentOverrideDataSchema } from "./aitm.schema.ts";
import { createAssignmentOverride, CreateAssignmentOverrideData } from "..";

export default tool({
  description: `
  Create an assignment override
One of student_ids, group_id, or course_section_id must be present. At
most
one should be present; if multiple are present only the most specific
(student_ids first, then
group_id, then course_section_id) is used and any
others are ignored.
    `,
  parameters: createAssignmentOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateAssignmentOverrideData, "url"> ) => {
    try {
      const { data } = await createAssignmentOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    