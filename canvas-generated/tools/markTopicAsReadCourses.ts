
import { tool } from "ai";
import { markTopicAsReadCoursesDataSchema } from "./aitm.schema.ts";
import { markTopicAsReadCourses, MarkTopicAsReadCoursesData } from "..";

export default tool({
  description: `
  Mark topic as read
Mark the initial text of the discussion topic as read.

No request fields are
necessary.

On success, the response will be 204 No Content with an empty body.
    `,
  parameters: markTopicAsReadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkTopicAsReadCoursesData, "url"> ) => {
    try {
      const { data } = await markTopicAsReadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    