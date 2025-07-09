
import { tool } from "ai";
import { updateMembershipMembershipsDataSchema } from "./aitm.schema.ts";
import { updateMembershipMemberships, UpdateMembershipMembershipsData } from "..";

export default tool({
  description: `
  Update a membership
Accept a membership request, or add/remove moderator rights.
    `,
  parameters: updateMembershipMembershipsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMembershipMembershipsData, "url"> ) => {
    try {
      const { data } = await updateMembershipMemberships(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    