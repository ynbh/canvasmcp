
import { tool } from "ai";
import { createLiveAssessmentResultsDataSchema } from "./aitm.schema.ts";
import { createLiveAssessmentResults, CreateLiveAssessmentResultsData } from "..";

export default tool({
  description: `
  Create live assessment results
Creates live assessment results and adds them to a live assessment
    `,
  parameters: createLiveAssessmentResultsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateLiveAssessmentResultsData, "url"> ) => {
    try {
      const { data } = await createLiveAssessmentResults(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    