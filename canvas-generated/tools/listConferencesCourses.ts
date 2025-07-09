
import { tool } from "ai";
import { listConferencesCoursesDataSchema } from "./aitm.schema.ts";
import { listConferencesCourses, ListConferencesCoursesData } from "..";

export default tool({
  description: `
  List conferences
Retrieve the paginated list of conferences for this context

This API returns a
JSON object containing the list of conferences,
the key for the list of conferences is "conferences"
    `,
  parameters: listConferencesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListConferencesCoursesData, "url"> ) => {
    try {
      const { data } = await listConferencesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    