
import { tool } from "ai";
import { updateSinglePollChoiceDataSchema } from "./aitm.schema.ts";
import { updateSinglePollChoice, UpdateSinglePollChoiceData } from "..";

export default tool({
  description: `
  Update a single poll choice
Update an existing poll choice for this poll
    `,
  parameters: updateSinglePollChoiceDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateSinglePollChoiceData, "url"> ) => {
    try {
      const { data } = await updateSinglePollChoice(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    