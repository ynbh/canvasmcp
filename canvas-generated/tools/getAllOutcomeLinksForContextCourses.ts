
import { tool } from "ai";
import { getAllOutcomeLinksForContextCoursesDataSchema } from "./aitm.schema.ts";
import { getAllOutcomeLinksForContextCourses, GetAllOutcomeLinksForContextCoursesData } from "..";

export default tool({
  description: `
  Get all outcome links for context
    `,
  parameters: getAllOutcomeLinksForContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllOutcomeLinksForContextCoursesData, "url"> ) => {
    try {
      const { data } = await getAllOutcomeLinksForContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    