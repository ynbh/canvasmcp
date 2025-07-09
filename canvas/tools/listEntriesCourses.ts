
import { tool } from "ai";
import { listEntriesCoursesDataSchema } from "./aitm.schema.ts";
import { listEntriesCourses, ListEntriesCoursesData } from "..";

export default tool({
  description: `
  List entries
Retrieve a paginated list of discussion entries, given a list of ids.

May require
(depending on the topic) that the user has posted in the topic.
If it is required, and the user has
not posted, will respond with a 403
Forbidden status and the body 'require_initial_post'.
    `,
  parameters: listEntriesCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEntriesCoursesData, "url"> ) => {
    try {
      const { data } = await listEntriesCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    