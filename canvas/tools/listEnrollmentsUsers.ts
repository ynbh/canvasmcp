
import { tool } from "ai";
import { listEnrollmentsUsersDataSchema } from "./aitm.schema.ts";
import { listEnrollmentsUsers, ListEnrollmentsUsersData } from "..";

export default tool({
  description: `
  List enrollments
Depending on the URL given, return a paginated list of Either (1) all of the
enrollments in a course, (2) all of the enrollments in a section or (3) all of a user's enrollments.
This includes student, teacher, TA, and observer enrollments. If a user has multiple enrollments in
a context (e.g. as a teacher and a student or in multiple course sections), each enrollment will be
listed separately. note: Currently, only a root level admin user can return other users'
enrollments. A user can, however, return his/her own enrollments.
    `,
  parameters: listEnrollmentsUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEnrollmentsUsersData, "url"> ) => {
    try {
      const { data } = await listEnrollmentsUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    