
import { tool } from "ai";
import { retrieveAssignmentOverriddenDatesForQuizzesDataSchema } from "./aitm.schema.ts";
import { retrieveAssignmentOverriddenDatesForQuizzes, RetrieveAssignmentOverriddenDatesForQuizzesData } from "..";

export default tool({
  description: `
  Retrieve assignment-overridden dates for quizzes
Retrieve the actual due-at, unlock-at, and
available-at dates for quizzes
based on the assignment overrides active for the current API user.
    `,
  parameters: retrieveAssignmentOverriddenDatesForQuizzesDataSchema.omit({ url: true }),
  execute: async (args : Omit<RetrieveAssignmentOverriddenDatesForQuizzesData, "url"> ) => {
    try {
      const { data } = await retrieveAssignmentOverriddenDatesForQuizzes(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    