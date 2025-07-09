
import { tool } from "ai";
import { listGroupMembershipsDataSchema } from "./aitm.schema.ts";
import { listGroupMemberships, ListGroupMembershipsData } from "..";

export default tool({
  description: `
  List group memberships
A paginated list of the members of a group.
    `,
  parameters: listGroupMembershipsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGroupMembershipsData, "url"> ) => {
    try {
      const { data } = await listGroupMemberships(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    