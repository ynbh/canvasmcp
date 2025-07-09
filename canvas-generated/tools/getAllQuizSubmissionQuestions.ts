
import { tool } from "ai";
import { getAllQuizSubmissionQuestionsDataSchema } from "./aitm.schema.ts";
import { getAllQuizSubmissionQuestions, GetAllQuizSubmissionQuestionsData } from "..";

export default tool({
  description: `
  Get all quiz submission questions.
Get a list of all the question records for this quiz
submission.

<b>200 OK</b> response code is returned if the request was successful.
    `,
  parameters: getAllQuizSubmissionQuestionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllQuizSubmissionQuestionsData, "url"> ) => {
    try {
      const { data } = await getAllQuizSubmissionQuestions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    