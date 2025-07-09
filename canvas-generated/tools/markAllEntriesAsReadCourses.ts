
import { tool } from "ai";
import { markAllEntriesAsReadCoursesDataSchema } from "./aitm.schema.ts";
import { markAllEntriesAsReadCourses, MarkAllEntriesAsReadCoursesData } from "..";

export default tool({
  description: `
  Mark all entries as read
Mark the discussion topic and all its entries as read.

No request fields
are necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markAllEntriesAsReadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkAllEntriesAsReadCoursesData, "url"> ) => {
    try {
      const { data } = await markAllEntriesAsReadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    