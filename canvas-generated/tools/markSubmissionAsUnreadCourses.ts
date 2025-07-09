
import { tool } from "ai";
import { markSubmissionAsUnreadCoursesDataSchema } from "./aitm.schema.ts";
import { markSubmissionAsUnreadCourses, MarkSubmissionAsUnreadCoursesData } from "..";

export default tool({
  description: `
  Mark submission as unread
No request fields are necessary.

On success, the response will be 204 No
Content with an empty body.
    `,
  parameters: markSubmissionAsUnreadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkSubmissionAsUnreadCoursesData, "url"> ) => {
    try {
      const { data } = await markSubmissionAsUnreadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    