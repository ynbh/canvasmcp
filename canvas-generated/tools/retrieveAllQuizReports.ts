
import { tool } from "ai";
import { retrieveAllQuizReportsDataSchema } from "./aitm.schema.ts";
import { retrieveAllQuizReports, RetrieveAllQuizReportsData } from "..";

export default tool({
  description: `
  Retrieve all quiz reports
Returns a list of all available reports.
    `,
  parameters: retrieveAllQuizReportsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RetrieveAllQuizReportsData, "url"> ) => {
    try {
      const { data } = await retrieveAllQuizReports(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    