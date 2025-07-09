
import { tool } from "ai";
import { destroyAssignmentGroupDataSchema } from "./aitm.schema.ts";
import { destroyAssignmentGroup, DestroyAssignmentGroupData } from "..";

export default tool({
  description: `
  Destroy an Assignment Group
Deletes the assignment group with the given id.
    `,
  parameters: destroyAssignmentGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<DestroyAssignmentGroupData, "url"> ) => {
    try {
      const { data } = await destroyAssignmentGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    