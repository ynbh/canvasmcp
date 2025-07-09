
import { tool } from "ai";
import { getSinglePollChoiceDataSchema } from "./aitm.schema.ts";
import { getSinglePollChoice, GetSinglePollChoiceData } from "..";

export default tool({
  description: `
  Get a single poll choice
Returns the poll choice with the given id
    `,
  parameters: getSinglePollChoiceDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSinglePollChoiceData, "url"> ) => {
    try {
      const { data } = await getSinglePollChoice(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    