
import { tool } from "ai";
import { listExternalToolsCoursesDataSchema } from "./aitm.schema.ts";
import { listExternalToolsCourses, ListExternalToolsCoursesData } from "..";

export default tool({
  description: `
  List external tools
Returns the paginated list of external tools for the current context.
See the
get request docs for a single tool for a list of properties on an external tool.
    `,
  parameters: listExternalToolsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListExternalToolsCoursesData, "url"> ) => {
    try {
      const { data } = await listExternalToolsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    