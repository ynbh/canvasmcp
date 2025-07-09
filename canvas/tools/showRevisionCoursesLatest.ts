
import { tool } from "ai";
import { showRevisionCoursesLatestDataSchema } from "./aitm.schema.ts";
import { showRevisionCoursesLatest, ShowRevisionCoursesLatestData } from "..";

export default tool({
  description: `
  Show revision
Retrieve the metadata and optionally content of a revision of the page.
Note that
retrieving historic versions of pages requires edit rights.
    `,
  parameters: showRevisionCoursesLatestDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowRevisionCoursesLatestData, "url"> ) => {
    try {
      const { data } = await showRevisionCoursesLatest(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    