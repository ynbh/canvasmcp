
import { tool } from "ai";
import { showFrontPageGroupsDataSchema } from "./aitm.schema.ts";
import { showFrontPageGroups, ShowFrontPageGroupsData } from "..";

export default tool({
  description: `
  Show front page
Retrieve the content of the front page
    `,
  parameters: showFrontPageGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowFrontPageGroupsData, "url"> ) => {
    try {
      const { data } = await showFrontPageGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    