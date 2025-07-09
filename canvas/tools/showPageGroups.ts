
import { tool } from "ai";
import { showPageGroupsDataSchema } from "./aitm.schema.ts";
import { showPageGroups, ShowPageGroupsData } from "..";

export default tool({
  description: `
  Show page
Retrieve the content of a wiki page
    `,
  parameters: showPageGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowPageGroupsData, "url"> ) => {
    try {
      const { data } = await showPageGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    