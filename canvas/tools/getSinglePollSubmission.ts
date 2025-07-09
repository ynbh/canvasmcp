
import { tool } from "ai";
import { getSinglePollSubmissionDataSchema } from "./aitm.schema.ts";
import { getSinglePollSubmission, GetSinglePollSubmissionData } from "..";

export default tool({
  description: `
  Get a single poll submission
Returns the poll submission with the given id
    `,
  parameters: getSinglePollSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSinglePollSubmissionData, "url"> ) => {
    try {
      const { data } = await getSinglePollSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    