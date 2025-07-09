
import { tool } from "ai";
import { showRevisionCoursesRevisionIdDataSchema } from "./aitm.schema.ts";
import { showRevisionCoursesRevisionId, ShowRevisionCoursesRevisionIdData } from "..";

export default tool({
  description: `
  Show revision
Retrieve the metadata and optionally content of a revision of the page.
Note that
retrieving historic versions of pages requires edit rights.
    `,
  parameters: showRevisionCoursesRevisionIdDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowRevisionCoursesRevisionIdData, "url"> ) => {
    try {
      const { data } = await showRevisionCoursesRevisionId(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    