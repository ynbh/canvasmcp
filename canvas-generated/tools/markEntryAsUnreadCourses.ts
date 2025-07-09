
import { tool } from "ai";
import { markEntryAsUnreadCoursesDataSchema } from "./aitm.schema.ts";
import { markEntryAsUnreadCourses, MarkEntryAsUnreadCoursesData } from "..";

export default tool({
  description: `
  Mark entry as unread
Mark a discussion entry as unread.

No request fields are necessary.

On
success, the response will be 204 No Content with an empty body.
    `,
  parameters: markEntryAsUnreadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkEntryAsUnreadCoursesData, "url"> ) => {
    try {
      const { data } = await markEntryAsUnreadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    