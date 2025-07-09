
import { tool } from "ai";
import { createMembershipDataSchema } from "./aitm.schema.ts";
import { createMembership, CreateMembershipData } from "..";

export default tool({
  description: `
  Create a membership
Join, or request to join, a group, depending on the join_level of the
group.  If
the membership or join request already exists, then it is simply
returned
    `,
  parameters: createMembershipDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateMembershipData, "url"> ) => {
    try {
      const { data } = await createMembership(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    