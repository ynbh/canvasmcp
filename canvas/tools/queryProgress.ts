
import { tool } from "ai";
import { queryProgressDataSchema } from "./aitm.schema.ts";
import { queryProgress, QueryProgressData } from "..";

export default tool({
  description: `
  Query progress
Return completion and status information about an asynchronous job
    `,
  parameters: queryProgressDataSchema.omit({ url: true }),
  execute: async (args : Omit<QueryProgressData, "url"> ) => {
    try {
      const { data } = await queryProgress(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    