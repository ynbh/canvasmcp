
import { tool } from "ai";
import { showOutcomeDataSchema } from "./aitm.schema.ts";
import { showOutcome, ShowOutcomeData } from "..";

export default tool({
  description: `
  Show an outcome
Returns the details of the outcome with the given id.
    `,
  parameters: showOutcomeDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowOutcomeData, "url"> ) => {
    try {
      const { data } = await showOutcome(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    