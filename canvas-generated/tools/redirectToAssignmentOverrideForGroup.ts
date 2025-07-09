
import { tool } from "ai";
import { redirectToAssignmentOverrideForGroupDataSchema } from "./aitm.schema.ts";
import { redirectToAssignmentOverrideForGroup, RedirectToAssignmentOverrideForGroupData } from "..";

export default tool({
  description: `
  Redirect to the assignment override for a group
Responds with a redirect to the override for the
given group, if any
(404 otherwise).
    `,
  parameters: redirectToAssignmentOverrideForGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<RedirectToAssignmentOverrideForGroupData, "url"> ) => {
    try {
      const { data } = await redirectToAssignmentOverrideForGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    