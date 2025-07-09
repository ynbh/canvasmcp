
import { tool } from "ai";
import { showContentExportUsersDataSchema } from "./aitm.schema.ts";
import { showContentExportUsers, ShowContentExportUsersData } from "..";

export default tool({
  description: `
  Show content export
Get information about a single content export.
    `,
  parameters: showContentExportUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowContentExportUsersData, "url"> ) => {
    try {
      const { data } = await showContentExportUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    