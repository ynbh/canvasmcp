
import { tool } from "ai";
import { listAvailableTabsForCourseOrGroupGroupsDataSchema } from "./aitm.schema.ts";
import { listAvailableTabsForCourseOrGroupGroups, ListAvailableTabsForCourseOrGroupGroupsData } from "..";

export default tool({
  description: `
  List available tabs for a course or group
Returns a paginated list of navigation tabs available in
the current context.
    `,
  parameters: listAvailableTabsForCourseOrGroupGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAvailableTabsForCourseOrGroupGroupsData, "url"> ) => {
    try {
      const { data } = await listAvailableTabsForCourseOrGroupGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    