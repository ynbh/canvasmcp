
import { tool } from "ai";
import { unlinkOutcomeCoursesDataSchema } from "./aitm.schema.ts";
import { unlinkOutcomeCourses, UnlinkOutcomeCoursesData } from "..";

export default tool({
  description: `
  Unlink an outcome
Unlinking an outcome only deletes the outcome itself if this was the last
link to
the outcome in any group in any context. Aligned outcomes cannot be
deleted; as such, if this is the
last link to an aligned outcome, the
unlinking will fail.
    `,
  parameters: unlinkOutcomeCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnlinkOutcomeCoursesData, "url"> ) => {
    try {
      const { data } = await unlinkOutcomeCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    