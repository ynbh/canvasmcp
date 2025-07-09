
import { tool } from "ai";
import { listQuizzesInCourseDataSchema } from "./aitm.schema.ts";
import { listQuizzesInCourse, ListQuizzesInCourseData } from "..";

export default tool({
  description: `
  List quizzes in a course
Returns the paginated list of Quizzes in this course.
    `,
  parameters: listQuizzesInCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListQuizzesInCourseData, "url"> ) => {
    try {
      const { data } = await listQuizzesInCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    