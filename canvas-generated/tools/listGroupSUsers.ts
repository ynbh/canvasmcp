
import { tool } from "ai";
import { listGroupSusersDataSchema } from "./aitm.schema.ts";
import { listGroupSUsers, ListGroupSusersData } from "..";

export default tool({
  description: `
  List group's users
Returns a paginated list of users in the group.
    `,
  parameters: listGroupSusersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGroupSusersData, "url"> ) => {
    try {
      const { data } = await listGroupSUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    