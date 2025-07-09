
import { tool } from "ai";
import { markSubmissionAsReadCoursesDataSchema } from "./aitm.schema.ts";
import { markSubmissionAsReadCourses, MarkSubmissionAsReadCoursesData } from "..";

export default tool({
  description: `
  Mark submission as read
No request fields are necessary.

On success, the response will be 204 No
Content with an empty body.
    `,
  parameters: markSubmissionAsReadCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkSubmissionAsReadCoursesData, "url"> ) => {
    try {
      const { data } = await markSubmissionAsReadCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    