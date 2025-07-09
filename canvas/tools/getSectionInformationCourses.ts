
import { tool } from "ai";
import { getSectionInformationCoursesDataSchema } from "./aitm.schema.ts";
import { getSectionInformationCourses, GetSectionInformationCoursesData } from "..";

export default tool({
  description: `
  Get section information
Gets details about a specific section
    `,
  parameters: getSectionInformationCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSectionInformationCoursesData, "url"> ) => {
    try {
      const { data } = await getSectionInformationCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    