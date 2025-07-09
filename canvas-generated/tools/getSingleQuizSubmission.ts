
import { tool } from "ai";
import { getSingleQuizSubmissionDataSchema } from "./aitm.schema.ts";
import { getSingleQuizSubmission, GetSingleQuizSubmissionData } from "..";

export default tool({
  description: `
  Get a single quiz submission.
Get a single quiz submission.

<b>200 OK</b> response code is returned
if the request was successful.
    `,
  parameters: getSingleQuizSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleQuizSubmissionData, "url"> ) => {
    try {
      const { data } = await getSingleQuizSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    