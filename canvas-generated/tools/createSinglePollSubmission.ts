
import { tool } from "ai";
import { createSinglePollSubmissionDataSchema } from "./aitm.schema.ts";
import { createSinglePollSubmission, CreateSinglePollSubmissionData } from "..";

export default tool({
  description: `
  Create a single poll submission
Create a new poll submission for this poll session
    `,
  parameters: createSinglePollSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSinglePollSubmissionData, "url"> ) => {
    try {
      const { data } = await createSinglePollSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    