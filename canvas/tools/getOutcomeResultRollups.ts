
import { tool } from "ai";
import { getOutcomeResultRollupsDataSchema } from "./aitm.schema.ts";
import { getOutcomeResultRollups, GetOutcomeResultRollupsData } from "..";

export default tool({
  description: `
  Get outcome result rollups
Gets the outcome rollups for the users and outcomes in the specified
context.
    `,
  parameters: getOutcomeResultRollupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetOutcomeResultRollupsData, "url"> ) => {
    try {
      const { data } = await getOutcomeResultRollups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    