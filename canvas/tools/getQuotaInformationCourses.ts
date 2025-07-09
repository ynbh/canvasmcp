
import { tool } from "ai";
import { getQuotaInformationCoursesDataSchema } from "./aitm.schema.ts";
import { getQuotaInformationCourses, GetQuotaInformationCoursesData } from "..";

export default tool({
  description: `
  Get quota information
Returns the total and used storage quota for the course, group, or user.
    `,
  parameters: getQuotaInformationCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetQuotaInformationCoursesData, "url"> ) => {
    try {
      const { data } = await getQuotaInformationCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    