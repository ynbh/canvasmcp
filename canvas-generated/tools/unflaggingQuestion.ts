
import { tool } from "ai";
import { unflaggingQuestionDataSchema } from "./aitm.schema.ts";
import { unflaggingQuestion, UnflaggingQuestionData } from "..";

export default tool({
  description: `
  Unflagging a question.
Remove the flag that you previously set on a quiz question after
you've
returned to it.
    `,
  parameters: unflaggingQuestionDataSchema.omit({ url: true }),
  execute: async (args : Omit<UnflaggingQuestionData, "url"> ) => {
    try {
      const { data } = await unflaggingQuestion(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    