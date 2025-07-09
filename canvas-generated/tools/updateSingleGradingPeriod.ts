
import { tool } from "ai";
import { updateSingleGradingPeriodDataSchema } from "./aitm.schema.ts";
import { updateSingleGradingPeriod, UpdateSingleGradingPeriodData } from "..";

export default tool({
  description: `
  Update a single grading period
Update an existing grading period.
    `,
  parameters: updateSingleGradingPeriodDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateSingleGradingPeriodData, "url"> ) => {
    try {
      const { data } = await updateSingleGradingPeriod(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    