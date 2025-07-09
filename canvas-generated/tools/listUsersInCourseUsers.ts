
import { tool } from "ai";
import { listUsersInCourseUsersDataSchema } from "./aitm.schema.ts";
import { listUsersInCourseUsers, ListUsersInCourseUsersData } from "..";

export default tool({
  description: `
  List users in course
Returns the paginated list of users in this course. And optionally the user's
enrollments in the course.
    `,
  parameters: listUsersInCourseUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListUsersInCourseUsersData, "url"> ) => {
    try {
      const { data } = await listUsersInCourseUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    