
import { tool } from "ai";
import { redirectToAssignmentOverrideForSectionDataSchema } from "./aitm.schema.ts";
import { redirectToAssignmentOverrideForSection, RedirectToAssignmentOverrideForSectionData } from "..";

export default tool({
  description: `
  Redirect to the assignment override for a section
Responds with a redirect to the override for the
given section, if any
(404 otherwise).
    `,
  parameters: redirectToAssignmentOverrideForSectionDataSchema.omit({ url: true }),
  execute: async (args : Omit<RedirectToAssignmentOverrideForSectionData, "url"> ) => {
    try {
      const { data } = await redirectToAssignmentOverrideForSection(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    