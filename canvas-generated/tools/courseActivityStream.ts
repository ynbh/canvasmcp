
import { tool } from "ai";
import { courseActivityStreamDataSchema } from "./aitm.schema.ts";
import { courseActivityStream, CourseActivityStreamData } from "..";

export default tool({
  description: `
  Course activity stream
Returns the current user's course-specific activity stream, paginated.

For
full documentation, see the API documentation for the user activity
stream, in the user api.
    `,
  parameters: courseActivityStreamDataSchema.omit({ url: true }),
  execute: async (args : Omit<CourseActivityStreamData, "url"> ) => {
    try {
      const { data } = await courseActivityStream(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    