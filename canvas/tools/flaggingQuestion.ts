
import { tool } from "ai";
import { flaggingQuestionDataSchema } from "./aitm.schema.ts";
import { flaggingQuestion, FlaggingQuestionData } from "..";

export default tool({
  description: `
  Flagging a question.
Set a flag on a quiz question to indicate that you want to return to it
later.
    `,
  parameters: flaggingQuestionDataSchema.omit({ url: true }),
  execute: async (args : Omit<FlaggingQuestionData, "url"> ) => {
    try {
      const { data } = await flaggingQuestion(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    