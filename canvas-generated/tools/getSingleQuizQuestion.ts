
import { tool } from "ai";
import { getSingleQuizQuestionDataSchema } from "./aitm.schema.ts";
import { getSingleQuizQuestion, GetSingleQuizQuestionData } from "..";

export default tool({
  description: `
  Get a single quiz question
Returns the quiz question with the given id
    `,
  parameters: getSingleQuizQuestionDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleQuizQuestionData, "url"> ) => {
    try {
      const { data } = await getSingleQuizQuestion(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    