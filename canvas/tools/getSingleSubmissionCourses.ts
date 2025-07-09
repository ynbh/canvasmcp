
import { tool } from "ai";
import { getSingleSubmissionCoursesDataSchema } from "./aitm.schema.ts";
import { getSingleSubmissionCourses, GetSingleSubmissionCoursesData } from "..";

export default tool({
  description: `
  Get a single submission
Get a single submission, based on user id.
    `,
  parameters: getSingleSubmissionCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleSubmissionCoursesData, "url"> ) => {
    try {
      const { data } = await getSingleSubmissionCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    