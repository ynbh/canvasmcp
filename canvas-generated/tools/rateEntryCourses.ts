
import { tool } from "ai";
import { rateEntryCoursesDataSchema } from "./aitm.schema.ts";
import { rateEntryCourses, RateEntryCoursesData } from "..";

export default tool({
  description: `
  Rate entry
Rate a discussion entry.

On success, the response will be 204 No Content with an empty
body.
    `,
  parameters: rateEntryCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RateEntryCoursesData, "url"> ) => {
    try {
      const { data } = await rateEntryCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    