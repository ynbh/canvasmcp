
import { tool } from "ai";
import { getAllQuizSubmissionsDataSchema } from "./aitm.schema.ts";
import { getAllQuizSubmissions, GetAllQuizSubmissionsData } from "..";

export default tool({
  description: `
  Get all quiz submissions.
Get a list of all submissions for this quiz. Users who can view or
manage
grades for a course will have submissions from multiple users returned. A
user who can only
submit will have only their own submissions returned. When
a user has an in-progress submission,
only that submission is returned. When
there isn't an in-progress quiz_submission, all completed
submissions,
including previous attempts, are returned.

<b>200 OK</b> response code is returned if
the request was successful.
    `,
  parameters: getAllQuizSubmissionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllQuizSubmissionsData, "url"> ) => {
    try {
      const { data } = await getAllQuizSubmissions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    