
import { tool } from "ai";
import { listCoursesForUserDataSchema } from "./aitm.schema.ts";
import { listCoursesForUser, ListCoursesForUserData } from "..";

export default tool({
  description: `
  List courses for a user
Returns a paginated list of active courses for this user. To view the course
list for a user other than yourself, you must be either an observer of that user or an
administrator.
    `,
  parameters: listCoursesForUserDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListCoursesForUserData, "url"> ) => {
    try {
      const { data } = await listCoursesForUser(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    