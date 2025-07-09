
import { tool } from "ai";
import { updateExistingQuizQuestionDataSchema } from "./aitm.schema.ts";
import { updateExistingQuizQuestion, UpdateExistingQuizQuestionData } from "..";

export default tool({
  description: `
  Update an existing quiz question
Updates an existing quiz question for this quiz
    `,
  parameters: updateExistingQuizQuestionDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateExistingQuizQuestionData, "url"> ) => {
    try {
      const { data } = await updateExistingQuizQuestion(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    