
import { tool } from "ai";
import { listLiveAssessmentResultsDataSchema } from "./aitm.schema.ts";
import { listLiveAssessmentResults, ListLiveAssessmentResultsData } from "..";

export default tool({
  description: `
  List live assessment results
Returns a paginated list of live assessment results
    `,
  parameters: listLiveAssessmentResultsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLiveAssessmentResultsData, "url"> ) => {
    try {
      const { data } = await listLiveAssessmentResults(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    