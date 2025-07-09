
import { tool } from "ai";
import { updateCourseDataSchema } from "./aitm.schema.ts";
import { updateCourse, UpdateCourseData } from "..";

export default tool({
  description: `
  Update a course
Update an existing course.

Arguments are the same as Courses#create, with a few
exceptions (enroll_me).

If a user has content management rights, but not full course editing
rights, the only attribute
editable through this endpoint will be "syllabus_body"
    `,
  parameters: updateCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCourseData, "url"> ) => {
    try {
      const { data } = await updateCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    