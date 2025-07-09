
import { tool } from "ai";
import { deleteExternalToolCoursesDataSchema } from "./aitm.schema.ts";
import { deleteExternalToolCourses, DeleteExternalToolCoursesData } from "..";

export default tool({
  description: `
  Delete an external tool
Remove the specified external tool
    `,
  parameters: deleteExternalToolCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteExternalToolCoursesData, "url"> ) => {
    try {
      const { data } = await deleteExternalToolCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    