
import { tool } from "ai";
import { createQuizDataSchema } from "./aitm.schema.ts";
import { createQuiz, CreateQuizData } from "..";

export default tool({
  description: `
  Create a quiz
Create a new quiz for this course.
    `,
  parameters: createQuizDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateQuizData, "url"> ) => {
    try {
      const { data } = await createQuiz(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    