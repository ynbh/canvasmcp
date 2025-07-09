
import { tool } from "ai";
import { getAllOutcomeGroupsForContextCoursesDataSchema } from "./aitm.schema.ts";
import { getAllOutcomeGroupsForContextCourses, GetAllOutcomeGroupsForContextCoursesData } from "..";

export default tool({
  description: `
  Get all outcome groups for context
    `,
  parameters: getAllOutcomeGroupsForContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllOutcomeGroupsForContextCoursesData, "url"> ) => {
    try {
      const { data } = await getAllOutcomeGroupsForContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    