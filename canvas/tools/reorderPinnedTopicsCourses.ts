
import { tool } from "ai";
import { reorderPinnedTopicsCoursesDataSchema } from "./aitm.schema.ts";
import { reorderPinnedTopicsCourses, ReorderPinnedTopicsCoursesData } from "..";

export default tool({
  description: `
  Reorder pinned topics
Puts the pinned discussion topics in the specified order.
All pinned topics
should be included.
    `,
  parameters: reorderPinnedTopicsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReorderPinnedTopicsCoursesData, "url"> ) => {
    try {
      const { data } = await reorderPinnedTopicsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    