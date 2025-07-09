
import { tool } from "ai";
import { createSinglePollChoiceDataSchema } from "./aitm.schema.ts";
import { createSinglePollChoice, CreateSinglePollChoiceData } from "..";

export default tool({
  description: `
  Create a single poll choice
Create a new poll choice for this poll
    `,
  parameters: createSinglePollChoiceDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateSinglePollChoiceData, "url"> ) => {
    try {
      const { data } = await createSinglePollChoice(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    