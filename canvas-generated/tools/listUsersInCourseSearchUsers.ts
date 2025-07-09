
import { tool } from "ai";
import { listUsersInCourseSearchUsersDataSchema } from "./aitm.schema.ts";
import { listUsersInCourseSearchUsers, ListUsersInCourseSearchUsersData } from "..";

export default tool({
  description: `
  List users in course
Returns the paginated list of users in this course. And optionally the user's
enrollments in the course.
    `,
  parameters: listUsersInCourseSearchUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUsersInCourseSearchUsersData, "url"> ) => {
    try {
      const { data } = await listUsersInCourseSearchUsers(args);
      console.log(data)
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    