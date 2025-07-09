
import { tool } from "ai";
import { markEntryAsReadCoursesDataSchema } from "./aitm.schema.ts";
import { markEntryAsReadCourses, MarkEntryAsReadCoursesData } from "..";

export default tool({
  description: `
  Mark entry as read
Mark a discussion entry as read.

No request fields are necessary.

On success,
the response will be 204 No Content with an empty body.
    `,
  parameters: markEntryAsReadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkEntryAsReadCoursesData, "url"> ) => {
    try {
      const { data } = await markEntryAsReadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    