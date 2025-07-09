
import { tool } from "ai";
import { markTopicAsUnreadCoursesDataSchema } from "./aitm.schema.ts";
import { markTopicAsUnreadCourses, MarkTopicAsUnreadCoursesData } from "..";

export default tool({
  description: `
  Mark topic as unread
Mark the initial text of the discussion topic as unread.

No request fields are
necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markTopicAsUnreadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkTopicAsUnreadCoursesData, "url"> ) => {
    try {
      const { data } = await markTopicAsUnreadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    