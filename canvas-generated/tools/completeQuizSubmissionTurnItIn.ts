
import { tool } from "ai";
import { completeQuizSubmissionTurnItInDataSchema } from "./aitm.schema.ts";
import { completeQuizSubmissionTurnItIn, CompleteQuizSubmissionTurnItInData } from "..";

export default tool({
  description: `
  Complete the quiz submission (turn it in).
Complete the quiz submission by marking it as complete
and grading it. When
the quiz submission has been marked as complete, no further modifications
will
be allowed.

<b>Responses</b>

* <b>200 OK</b> if the request was successful
* <b>403 Forbidden</b>
if an invalid access code is specified
* <b>403 Forbidden</b> if the Quiz's IP filter restriction
does not pass
* <b>403 Forbidden</b> if an invalid token is specified
* <b>400 Bad Request</b> if
the QS is already complete
* <b>400 Bad Request</b> if the attempt parameter is missing
* <b>400 Bad
Request</b> if the attempt parameter is not the latest attempt
    `,
  parameters: completeQuizSubmissionTurnItInDataSchema.omit({ url: true }),
  execute: async (args : Omit<CompleteQuizSubmissionTurnItInData, "url"> ) => {
    try {
      const { data } = await completeQuizSubmissionTurnItIn(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    