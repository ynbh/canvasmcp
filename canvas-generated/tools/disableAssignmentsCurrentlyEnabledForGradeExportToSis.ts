
import { tool } from "ai";
import { disableAssignmentsCurrentlyEnabledForGradeExportToSisDataSchema } from "./aitm.schema.ts";
import { disableAssignmentsCurrentlyEnabledForGradeExportToSis, DisableAssignmentsCurrentlyEnabledForGradeExportToSisData } from "..";

export default tool({
  description: `
  Disable assignments currently enabled for grade export to SIS
Disable all assignments flagged as
"post_to_sis", with the option of making it
specific to a grading period, in a course.

On success,
the response will be 204 No Content with an empty body.

On failure, the response will be 400 Bad
Request with a body of a specific
message.

For disabling assignments in a specific grading period
    `,
  parameters: disableAssignmentsCurrentlyEnabledForGradeExportToSisDataSchema.omit({ url: true }),
  execute: async (args : Omit<DisableAssignmentsCurrentlyEnabledForGradeExportToSisData, "url"> ) => {
    try {
      const { data } = await disableAssignmentsCurrentlyEnabledForGradeExportToSis(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    