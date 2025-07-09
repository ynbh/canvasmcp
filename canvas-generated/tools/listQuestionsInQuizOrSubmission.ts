
import { tool } from "ai";
import { listQuestionsInQuizOrSubmissionDataSchema } from "./aitm.schema.ts";
import { listQuestionsInQuizOrSubmission, ListQuestionsInQuizOrSubmissionData } from "..";

export default tool({
  description: `
  List questions in a quiz or a submission
Returns the paginated list of QuizQuestions in this quiz.
    `,
  parameters: listQuestionsInQuizOrSubmissionDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListQuestionsInQuizOrSubmissionData, "url"> ) => {
    try {
      const { data } = await listQuestionsInQuizOrSubmission(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    