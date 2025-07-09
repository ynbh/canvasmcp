
import { tool } from "ai";
import { redirectToRootOutcomeGroupForContextCoursesDataSchema } from "./aitm.schema.ts";
import { redirectToRootOutcomeGroupForContextCourses, RedirectToRootOutcomeGroupForContextCoursesData } from "..";

export default tool({
  description: `
  Redirect to root outcome group for context
Convenience redirect to find the root outcome group for a
particular
context. Will redirect to the appropriate outcome group's URL.
    `,
  parameters: redirectToRootOutcomeGroupForContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RedirectToRootOutcomeGroupForContextCoursesData, "url"> ) => {
    try {
      const { data } = await redirectToRootOutcomeGroupForContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    