
import { tool } from "ai";
import { getSingleSubmissionDataSchema } from "./aitm.schema.ts";
import { getSingleSubmission, GetSingleSubmissionData } from "..";

export default tool({
  description: `
  Get a single submission
Get a single submission, based on submission id.
    `,
  parameters: getSingleSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleSubmissionData, "url"> ) => {
    try {
      const { data } = await getSingleSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    