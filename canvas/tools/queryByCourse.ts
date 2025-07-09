
import { tool } from "ai";
import { queryByCourseDataSchema } from "./aitm.schema.ts";
import { queryByCourse, QueryByCourseData } from "..";

export default tool({
  description: `
  Query by course.
List course change events for a given course.
    `,
  parameters: queryByCourseDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByCourseData, "url"> ) => {
    try {
      const { data } = await queryByCourse(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    