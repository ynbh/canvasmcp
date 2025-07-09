
import { tool } from "ai";
import { showRevisionGroupsLatestDataSchema } from "./aitm.schema.ts";
import { showRevisionGroupsLatest, ShowRevisionGroupsLatestData } from "..";

export default tool({
  description: `
  Show revision
Retrieve the metadata and optionally content of a revision of the page.
Note that
retrieving historic versions of pages requires edit rights.
    `,
  parameters: showRevisionGroupsLatestDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowRevisionGroupsLatestData, "url"> ) => {
    try {
      const { data } = await showRevisionGroupsLatest(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    