
import { tool } from "ai";
import { getSingleRubricCoursesDataSchema } from "./aitm.schema.ts";
import { getSingleRubricCourses, GetSingleRubricCoursesData } from "..";

export default tool({
  description: `
  Get a single rubric
Returns the rubric with the given id.
    `,
  parameters: getSingleRubricCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleRubricCoursesData, "url"> ) => {
    try {
      const { data } = await getSingleRubricCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    