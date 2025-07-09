
import { tool } from "ai";
import { createSingleQuizQuestionDataSchema } from "./aitm.schema.ts";
import { createSingleQuizQuestion, CreateSingleQuizQuestionData } from "..";

export default tool({
  description: `
  Create a single quiz question
Create a new quiz question for this quiz
    `,
  parameters: createSingleQuizQuestionDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSingleQuizQuestionData, "url"> ) => {
    try {
      const { data } = await createSingleQuizQuestion(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    