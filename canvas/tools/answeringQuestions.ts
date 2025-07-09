
import { tool } from "ai";
import { answeringQuestionsDataSchema } from "./aitm.schema.ts";
import { answeringQuestions, AnsweringQuestionsData } from "..";

export default tool({
  description: `
  Answering questions
Provide or update an answer to one or more QuizQuestions.
    `,
  parameters: answeringQuestionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<AnsweringQuestionsData, "url"> ) => {
    try {
      const { data } = await answeringQuestions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    