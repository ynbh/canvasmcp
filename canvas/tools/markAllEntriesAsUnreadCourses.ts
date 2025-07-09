
import { tool } from "ai";
import { markAllEntriesAsUnreadCoursesDataSchema } from "./aitm.schema.ts";
import { markAllEntriesAsUnreadCourses, MarkAllEntriesAsUnreadCoursesData } from "..";

export default tool({
  description: `
  Mark all entries as unread
Mark the discussion topic and all its entries as unread.

No request
fields are necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markAllEntriesAsUnreadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkAllEntriesAsUnreadCoursesData, "url"> ) => {
    try {
      const { data } = await markAllEntriesAsUnreadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    