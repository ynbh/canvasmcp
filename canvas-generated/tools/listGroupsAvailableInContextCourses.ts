
import { tool } from "ai";
import { listGroupsAvailableInContextCoursesDataSchema } from "./aitm.schema.ts";
import { listGroupsAvailableInContextCourses, ListGroupsAvailableInContextCoursesData } from "..";

export default tool({
  description: `
  List the groups available in a context.
Returns the paginated list of active groups in the given
context that are visible to user.
    `,
  parameters: listGroupsAvailableInContextCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListGroupsAvailableInContextCoursesData, "url"> ) => {
    try {
      const { data } = await listGroupsAvailableInContextCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    