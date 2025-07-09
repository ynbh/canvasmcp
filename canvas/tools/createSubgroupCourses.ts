
import { tool } from "ai";
import { createSubgroupCoursesDataSchema } from "./aitm.schema.ts";
import { createSubgroupCourses, CreateSubgroupCoursesData } from "..";

export default tool({
  description: `
  Create a subgroup
Creates a new empty subgroup under the outcome group with the given title
and
description.
    `,
  parameters: createSubgroupCoursesDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSubgroupCoursesData, "url"> ) => {
    try {
      const { data } = await createSubgroupCourses(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    