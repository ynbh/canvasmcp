
import { tool } from "ai";
import { createCourseSectionDataSchema } from "./aitm.schema.ts";
import { createCourseSection, CreateCourseSectionData } from "..";

export default tool({
  description: `
  Create course section
Creates a new section for this course.
    `,
  parameters: createCourseSectionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateCourseSectionData, "url"> ) => {
    try {
      const { data } = await createCourseSection(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    