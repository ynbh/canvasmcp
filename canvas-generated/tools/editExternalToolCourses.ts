
import { tool } from "ai";
import { editExternalToolCoursesDataSchema } from "./aitm.schema.ts";
import { editExternalToolCourses, EditExternalToolCoursesData } from "..";

export default tool({
  description: `
  Edit an external tool
Update the specified external tool. Uses same parameters as create
    `,
  parameters: editExternalToolCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditExternalToolCoursesData, "url"> ) => {
    try {
      const { data } = await editExternalToolCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    