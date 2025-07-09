
import { tool } from "ai";
import { listLiveAssessmentsDataSchema } from "./aitm.schema.ts";
import { listLiveAssessments, ListLiveAssessmentsData } from "..";

export default tool({
  description: `
  List live assessments
Returns a paginated list of live assessments.
    `,
  parameters: listLiveAssessmentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListLiveAssessmentsData, "url"> ) => {
    try {
      const { data } = await listLiveAssessments(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    