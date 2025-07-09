
import { tool } from "ai";
import { revertToRevisionGroupsDataSchema } from "./aitm.schema.ts";
import { revertToRevisionGroups, RevertToRevisionGroupsData } from "..";

export default tool({
  description: `
  Revert to revision
Revert a page to a prior revision.
    `,
  parameters: revertToRevisionGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RevertToRevisionGroupsData, "url"> ) => {
    try {
      const { data } = await revertToRevisionGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    