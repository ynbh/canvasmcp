
import { tool } from "ai";
import { listContentExportsGroupsDataSchema } from "./aitm.schema.ts";
import { listContentExportsGroups, ListContentExportsGroupsData } from "..";

export default tool({
  description: `
  List content exports
A paginated list of the past and pending content export jobs for a
course,
group, or user. Exports are returned newest first.
    `,
  parameters: listContentExportsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListContentExportsGroupsData, "url"> ) => {
    try {
      const { data } = await listContentExportsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    