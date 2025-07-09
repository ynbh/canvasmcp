
import { tool } from "ai";
import { reorderPinnedTopicsGroupsDataSchema } from "./aitm.schema.ts";
import { reorderPinnedTopicsGroups, ReorderPinnedTopicsGroupsData } from "..";

export default tool({
  description: `
  Reorder pinned topics
Puts the pinned discussion topics in the specified order.
All pinned topics
should be included.
    `,
  parameters: reorderPinnedTopicsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReorderPinnedTopicsGroupsData, "url"> ) => {
    try {
      const { data } = await reorderPinnedTopicsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    