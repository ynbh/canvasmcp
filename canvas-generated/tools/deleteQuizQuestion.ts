
import { tool } from "ai";
import { deleteQuizQuestionDataSchema } from "./aitm.schema.ts";
import { deleteQuizQuestion, DeleteQuizQuestionData } from "..";

export default tool({
  description: `
  Delete a quiz question
<b>204 No Content</b> response code is returned if the deletion was
successful.
    `,
  parameters: deleteQuizQuestionDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteQuizQuestionData, "url"> ) => {
    try {
      const { data } = await deleteQuizQuestion(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    