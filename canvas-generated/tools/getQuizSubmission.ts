
import { tool } from "ai";
import { getQuizSubmissionDataSchema } from "./aitm.schema.ts";
import { getQuizSubmission, GetQuizSubmissionData } from "..";

export default tool({
  description: `
  Get the quiz submission.
Get the submission for this quiz for the current user.

<b>200 OK</b>
response code is returned if the request was successful.
    `,
  parameters: getQuizSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetQuizSubmissionData, "url"> ) => {
    try {
      const { data } = await getQuizSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    