
import { tool } from "ai";
import { batchRetrieveOverridesInCourseDataSchema } from "./aitm.schema.ts";
import { batchRetrieveOverridesInCourse, BatchRetrieveOverridesInCourseData } from "..";

export default tool({
  description: `
  Batch retrieve overrides in a course
Returns a list of specified overrides in this course,
providing
they target sections/groups/students visible to the current user.
Returns null elements in
the list for requests that were not found.
    `,
  parameters: batchRetrieveOverridesInCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<BatchRetrieveOverridesInCourseData, "url"> ) => {
    try {
      const { data } = await batchRetrieveOverridesInCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    