
import { tool } from "ai";
import { getAssignmentGroupDataSchema } from "./aitm.schema.ts";
import { getAssignmentGroup, GetAssignmentGroupData } from "..";

export default tool({
  description: `
  Get an Assignment Group
Returns the assignment group with the given id.
    `,
  parameters: getAssignmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAssignmentGroupData, "url"> ) => {
    try {
      const { data } = await getAssignmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    