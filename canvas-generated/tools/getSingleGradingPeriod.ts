
import { tool } from "ai";
import { getSingleGradingPeriodDataSchema } from "./aitm.schema.ts";
import { getSingleGradingPeriod, GetSingleGradingPeriodData } from "..";

export default tool({
  description: `
  Get a single grading period
Returns the grading period with the given id
    `,
  parameters: getSingleGradingPeriodDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGradingPeriodData, "url"> ) => {
    try {
      const { data } = await getSingleGradingPeriod(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    