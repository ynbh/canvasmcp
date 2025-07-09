
import { tool } from "ai";
import { showOutcomeGroupCoursesDataSchema } from "./aitm.schema.ts";
import { showOutcomeGroupCourses, ShowOutcomeGroupCoursesData } from "..";

export default tool({
  description: `
  Show an outcome group
    `,
  parameters: showOutcomeGroupCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowOutcomeGroupCoursesData, "url"> ) => {
    try {
      const { data } = await showOutcomeGroupCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    