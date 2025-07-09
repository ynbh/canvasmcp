
import { tool } from "ai";
import { getHistoryOfSingleSubmissionDataSchema } from "./aitm.schema.ts";
import { getHistoryOfSingleSubmission, GetHistoryOfSingleSubmissionData } from "..";

export default tool({
  description: `
  Get the history of a single submission
Get a list of all attempts made for a submission, based on
submission id.
    `,
  parameters: getHistoryOfSingleSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetHistoryOfSingleSubmissionData, "url"> ) => {
    try {
      const { data } = await getHistoryOfSingleSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    