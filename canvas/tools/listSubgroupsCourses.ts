
import { tool } from "ai";
import { listSubgroupsCoursesDataSchema } from "./aitm.schema.ts";
import { listSubgroupsCourses, ListSubgroupsCoursesData } from "..";

export default tool({
  description: `
  List subgroups
A paginated list of the immediate OutcomeGroup children of the outcome group.
    `,
  parameters: listSubgroupsCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListSubgroupsCoursesData, "url"> ) => {
    try {
      const { data } = await listSubgroupsCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    