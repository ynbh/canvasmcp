
import { tool } from "ai";
import { createQuestionGroupDataSchema } from "./aitm.schema.ts";
import { createQuestionGroup, CreateQuestionGroupData } from "..";

export default tool({
  description: `
  Create a question group
Create a new question group for this quiz

<b>201 Created</b> response code
is returned if the creation was successful.
    `,
  parameters: createQuestionGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateQuestionGroupData, "url"> ) => {
    try {
      const { data } = await createQuestionGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    