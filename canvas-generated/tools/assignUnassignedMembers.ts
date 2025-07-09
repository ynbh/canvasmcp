
import { tool } from "ai";
import { assignUnassignedMembersDataSchema } from "./aitm.schema.ts";
import { assignUnassignedMembers, AssignUnassignedMembersData } from "..";

export default tool({
  description: `
  Assign unassigned members
Assign all unassigned members as evenly as possible among the
existing
student groups.
    `,
  parameters: assignUnassignedMembersDataSchema.omit({ url: true }),
  execute: async (args : Omit<AssignUnassignedMembersData, "url"> ) => {
    try {
      const { data } = await assignUnassignedMembers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    