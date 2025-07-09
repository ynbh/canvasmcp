
import { tool } from "ai";
import { showRevisionGroupsRevisionIdDataSchema } from "./aitm.schema.ts";
import { showRevisionGroupsRevisionId, ShowRevisionGroupsRevisionIdData } from "..";

export default tool({
  description: `
  Show revision
Retrieve the metadata and optionally content of a revision of the page.
Note that
retrieving historic versions of pages requires edit rights.
    `,
  parameters: showRevisionGroupsRevisionIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowRevisionGroupsRevisionIdData, "url"> ) => {
    try {
      const { data } = await showRevisionGroupsRevisionId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    