
import { tool } from "ai";
import { getSingleGroupMembershipMembershipsDataSchema } from "./aitm.schema.ts";
import { getSingleGroupMembershipMemberships, GetSingleGroupMembershipMembershipsData } from "..";

export default tool({
  description: `
  Get a single group membership
Returns the group membership with the given membership id or user id.
    `,
  parameters: getSingleGroupMembershipMembershipsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGroupMembershipMembershipsData, "url"> ) => {
    try {
      const { data } = await getSingleGroupMembershipMemberships(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    