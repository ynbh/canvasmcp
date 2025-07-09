
import { tool } from "ai";
import { createQuizSubmissionStartQuizTakingSessionDataSchema } from "./aitm.schema.ts";
import { createQuizSubmissionStartQuizTakingSession, CreateQuizSubmissionStartQuizTakingSessionData } from "..";

export default tool({
  description: `
  Create the quiz submission (start a quiz-taking session)
Start taking a Quiz by creating a
QuizSubmission which you can use to answer
questions and submit your answers.

<b>Responses</b>

*
<b>200 OK</b> if the request was successful
* <b>400 Bad Request</b> if the quiz is locked
* <b>403
Forbidden</b> if an invalid access code is specified
* <b>403 Forbidden</b> if the Quiz's IP filter
restriction does not pass
* <b>409 Conflict</b> if a QuizSubmission already exists for this user and
quiz
    `,
  parameters: createQuizSubmissionStartQuizTakingSessionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateQuizSubmissionStartQuizTakingSessionData, "url"> ) => {
    try {
      const { data } = await createQuizSubmissionStartQuizTakingSession(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    