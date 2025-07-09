
import { tool } from "ai";
import { updateAssociatedCoursesDataSchema } from "./aitm.schema.ts";
import { updateAssociatedCourses, UpdateAssociatedCoursesData } from "..";

export default tool({
  description: `
  Update associated courses
Send a list of course ids to add or remove new associations for the
template.
Cannot add courses that do not belong to the blueprint course's account. Also cannot
add
other blueprint courses or courses that already have an association with another blueprint
course.
    `,
  parameters: updateAssociatedCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateAssociatedCoursesData, "url"> ) => {
    try {
      const { data } = await updateAssociatedCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    