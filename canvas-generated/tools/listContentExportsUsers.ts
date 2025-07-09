
import { tool } from "ai";
import { listContentExportsUsersDataSchema } from "./aitm.schema.ts";
import { listContentExportsUsers, ListContentExportsUsersData } from "..";

export default tool({
  description: `
  List content exports
A paginated list of the past and pending content export jobs for a
course,
group, or user. Exports are returned newest first.
    `,
  parameters: listContentExportsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentExportsUsersData, "url"> ) => {
    try {
      const { data } = await listContentExportsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    