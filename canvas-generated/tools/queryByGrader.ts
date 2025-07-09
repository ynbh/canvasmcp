
import { tool } from "ai";
import { queryByGraderDataSchema } from "./aitm.schema.ts";
import { queryByGrader, QueryByGraderData } from "..";

export default tool({
  description: `
  Query by grader.
List grade change events for a given grader.
    `,
  parameters: queryByGraderDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryByGraderData, "url"> ) => {
    try {
      const { data } = await queryByGrader(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    