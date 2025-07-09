
import { tool } from "ai";
import { deleteQuizDataSchema } from "./aitm.schema.ts";
import { deleteQuiz, DeleteQuizData } from "..";

export default tool({
  description: `
  Delete a quiz
    `,
  parameters: deleteQuizDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteQuizData, "url"> ) => {
    try {
      const { data } = await deleteQuiz(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    