
import { tool } from "ai";
import { createExternalToolCoursesDataSchema } from "./aitm.schema.ts";
import { createExternalToolCourses, CreateExternalToolCoursesData } from "..";

export default tool({
  description: `
  Create an external tool
Create an external tool in the specified course/account.
The created tool
will be returned, see the "show" endpoint for an example.
    `,
  parameters: createExternalToolCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateExternalToolCoursesData, "url"> ) => {
    try {
      const { data } = await createExternalToolCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    