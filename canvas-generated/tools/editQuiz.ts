
import { tool } from "ai";
import { editQuizDataSchema } from "./aitm.schema.ts";
import { editQuiz, EditQuizData } from "..";

export default tool({
  description: `
  Edit a quiz
Modify an existing quiz. See the documentation for quiz creation.

Additional arguments:
    `,
  parameters: editQuizDataSchema.omit({ url: true }),
  execute: async (args : Omit<EditQuizData, "url"> ) => {
    try {
      const { data } = await editQuiz(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    