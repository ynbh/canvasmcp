
import { tool } from "ai";
import { getSingleQuizDataSchema } from "./aitm.schema.ts";
import { getSingleQuiz, GetSingleQuizData } from "..";

export default tool({
  description: `
  Get a single quiz
Returns the quiz with the given id.
    `,
  parameters: getSingleQuizDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleQuizData, "url"> ) => {
    try {
      const { data } = await getSingleQuiz(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    