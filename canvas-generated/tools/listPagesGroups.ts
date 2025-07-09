
import { tool } from "ai";
import { listPagesGroupsDataSchema } from "./aitm.schema.ts";
import { listPagesGroups, ListPagesGroupsData } from "..";

export default tool({
  description: `
  List pages
A paginated list of the wiki pages associated with a course or group
    `,
  parameters: listPagesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListPagesGroupsData, "url"> ) => {
    try {
      const { data } = await listPagesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    