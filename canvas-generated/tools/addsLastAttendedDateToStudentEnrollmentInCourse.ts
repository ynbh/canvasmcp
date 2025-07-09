
import { tool } from "ai";
import { addsLastAttendedDateToStudentEnrollmentInCourseDataSchema } from "./aitm.schema.ts";
import { addsLastAttendedDateToStudentEnrollmentInCourse, AddsLastAttendedDateToStudentEnrollmentInCourseData } from "..";

export default tool({
  description: `
  Adds last attended date to student enrollment in course
    `,
  parameters: addsLastAttendedDateToStudentEnrollmentInCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddsLastAttendedDateToStudentEnrollmentInCourseData, "url"> ) => {
    try {
      const { data } = await addsLastAttendedDateToStudentEnrollmentInCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    