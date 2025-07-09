
import { tool } from "ai";
import { listAvailableTabsForCourseOrGroupCoursesDataSchema } from "./aitm.schema.ts";
import { listAvailableTabsForCourseOrGroupCourses, ListAvailableTabsForCourseOrGroupCoursesData } from "..";

export default tool({
  description: `
  List available tabs for a course or group
Returns a paginated list of navigation tabs available in
the current context.
    `,
  parameters: listAvailableTabsForCourseOrGroupCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAvailableTabsForCourseOrGroupCoursesData, "url"> ) => {
    try {
      const { data } = await listAvailableTabsForCourseOrGroupCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    