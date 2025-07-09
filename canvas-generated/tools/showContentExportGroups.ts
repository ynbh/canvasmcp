
import { tool } from "ai";
import { showContentExportGroupsDataSchema } from "./aitm.schema.ts";
import { showContentExportGroups, ShowContentExportGroupsData } from "..";

export default tool({
  description: `
  Show content export
Get information about a single content export.
    `,
  parameters: showContentExportGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowContentExportGroupsData, "url"> ) => {
    try {
      const { data } = await showContentExportGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    