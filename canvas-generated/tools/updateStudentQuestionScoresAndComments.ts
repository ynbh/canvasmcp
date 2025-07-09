
import { tool } from "ai";
import { updateStudentQuestionScoresAndCommentsDataSchema } from "./aitm.schema.ts";
import { updateStudentQuestionScoresAndComments, UpdateStudentQuestionScoresAndCommentsData } from "..";

export default tool({
  description: `
  Update student question scores and comments.
Update the amount of points a student has scored for
questions they've
answered, provide comments for the student about their answer(s), or simply
fudge
the total score by a specific amount of points.

<b>Responses</b>

* <b>200 OK</b> if the request
was successful
* <b>403 Forbidden</b> if you are not a teacher in this course
* <b>400 Bad
Request</b> if the attempt parameter is missing or invalid
* <b>400 Bad Request</b> if the specified
QS attempt is not yet complete
    `,
  parameters: updateStudentQuestionScoresAndCommentsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateStudentQuestionScoresAndCommentsData, "url"> ) => {
    try {
      const { data } = await updateStudentQuestionScoresAndComments(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    