
import { tool } from "ai";
import { updateMembershipUsersDataSchema } from "./aitm.schema.ts";
import { updateMembershipUsers, UpdateMembershipUsersData } from "..";

export default tool({
  description: `
  Update a membership
Accept a membership request, or add/remove moderator rights.
    `,
  parameters: updateMembershipUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateMembershipUsersData, "url"> ) => {
    try {
      const { data } = await updateMembershipUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    