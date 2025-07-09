
import { tool } from "ai";
import { listYourGroupsDataSchema } from "./aitm.schema.ts";
import { listYourGroups, ListYourGroupsData } from "..";

export default tool({
  description: `
  List your groups
Returns a paginated list of active groups for the current user.
    `,
  parameters: listYourGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListYourGroupsData, "url"> ) => {
    try {
      const { data } = await listYourGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    