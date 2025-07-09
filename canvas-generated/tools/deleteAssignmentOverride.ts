
import { tool } from "ai";
import { deleteAssignmentOverrideDataSchema } from "./aitm.schema.ts";
import { deleteAssignmentOverride, DeleteAssignmentOverrideData } from "..";

export default tool({
  description: `
  Delete an assignment override
Deletes an override and returns its former details.
    `,
  parameters: deleteAssignmentOverrideDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteAssignmentOverrideData, "url"> ) => {
    try {
      const { data } = await deleteAssignmentOverride(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    