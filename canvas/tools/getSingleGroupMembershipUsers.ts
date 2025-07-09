
import { tool } from "ai";
import { getSingleGroupMembershipUsersDataSchema } from "./aitm.schema.ts";
import { getSingleGroupMembershipUsers, GetSingleGroupMembershipUsersData } from "..";

export default tool({
  description: `
  Get a single group membership
Returns the group membership with the given membership id or user id.
    `,
  parameters: getSingleGroupMembershipUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGroupMembershipUsersData, "url"> ) => {
    try {
      const { data } = await getSingleGroupMembershipUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    