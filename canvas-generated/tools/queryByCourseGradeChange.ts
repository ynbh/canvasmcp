
import { tool } from "ai";
import { queryByCourseGradeChangeDataSchema } from "./aitm.schema.ts";
import { queryByCourseGradeChange, QueryByCourseGradeChangeData } from "..";

export default tool({
  description: `
  Query by course.
List grade change events for a given course.
    `,
  parameters: queryByCourseGradeChangeDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByCourseGradeChangeData, "url"> ) => {
    try {
      const { data } = await queryByCourseGradeChange(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    