
import { tool } from "ai";
import { getSessionlessLaunchUrlForExternalToolCoursesDataSchema } from "./aitm.schema.ts";
import { getSessionlessLaunchUrlForExternalToolCourses, GetSessionlessLaunchUrlForExternalToolCoursesData } from "..";

export default tool({
  description: `
  Get a sessionless launch url for an external tool.
Returns a sessionless launch url for an external
tool.

NOTE: Either the id or url must be provided unless launch_type is assessment or module_item.
    `,
  parameters: getSessionlessLaunchUrlForExternalToolCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSessionlessLaunchUrlForExternalToolCoursesData, "url"> ) => {
    try {
      const { data } = await getSessionlessLaunchUrlForExternalToolCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    