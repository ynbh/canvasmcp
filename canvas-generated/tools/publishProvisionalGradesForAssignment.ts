
import { tool } from "ai";
import { publishProvisionalGradesForAssignmentDataSchema } from "./aitm.schema.ts";
import { publishProvisionalGradesForAssignment, PublishProvisionalGradesForAssignmentData } from "..";

export default tool({
  description: `
  Publish provisional grades for an assignment
Publish the selected provisional grade for all
submissions to an assignment.
Use the "Select provisional grade" endpoint to choose which
provisional grade to publish
for a particular submission.

Students not in the moderation set will
have their one and only provisional grade published.

WARNING: This is irreversible. This will
overwrite existing grades in the gradebook.
    `,
  parameters: publishProvisionalGradesForAssignmentDataSchema.omit({ url: true }),
  execute: async (args : Omit<PublishProvisionalGradesForAssignmentData, "url"> ) => {
    try {
      const { data } = await publishProvisionalGradesForAssignment(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    