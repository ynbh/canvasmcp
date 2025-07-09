
import { tool } from "ai";
import { listEnrollmentsCoursesDataSchema } from "./aitm.schema.ts";
import { listEnrollmentsCourses, ListEnrollmentsCoursesData } from "..";

export default tool({
  description: `
  List enrollments
Depending on the URL given, return a paginated list of either (1) all of the
enrollments in a course, (2) all of the enrollments in a section or (3) all of a user's enrollments.
This includes student, teacher, TA, and
observer enrollments.

If a user has multiple enrollments in
a context (e.g. as a teacher
and a student or in multiple course sections), each enrollment will
be
listed separately.

note: Currently, only a root level admin user can return other users'
enrollments. A
user can, however, return his/her own enrollments.
    `,
  parameters: listEnrollmentsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListEnrollmentsCoursesData, "url"> ) => {
    try {
      const { data } = await listEnrollmentsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    