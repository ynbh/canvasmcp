
import { tool } from "ai";
import { updateCoursesDataSchema } from "./aitm.schema.ts";
import { updateCourses, UpdateCoursesData } from "..";

export default tool({
  description: `
  Update courses
Update multiple courses in an account.  Operates asynchronously; use the
{api:ProgressController#show progress endpoint}
to query the status of an operation.

The action to
take on each course.  Must be one of 'offer', 'conclude', 'delete', or 'undelete'.
* 'offer' makes a
course visible to students. This action is also called "publish" on the web site.
* 'conclude'
prevents future enrollments and makes a course read-only for all participants. The course still
appears
in prior-enrollment lists.
* 'delete' completely removes the course from the web site
(including course menus and prior-enrollment lists).
All enrollments are deleted. Course content may
be physically deleted at a future date.
* 'undelete' attempts to recover a course that has been
deleted. (Recovery is not guaranteed; please conclude
rather than delete a course if there is any
possibility the course will be used again.) The recovered course
will be unpublished. Deleted
enrollments will not be recovered.
    `,
  parameters: updateCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCoursesData, "url"> ) => {
    try {
      const { data } = await updateCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    