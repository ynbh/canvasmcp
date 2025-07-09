
import { tool } from "ai";
import { getSingleGroupDataSchema } from "./aitm.schema.ts";
import { getSingleGroup, GetSingleGroupData } from "..";

export default tool({
  description: `
  Get a single group
Returns the data for a single group, or a 401 if the caller doesn't have
the
rights to see it.
    `,
  parameters: getSingleGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetSingleGroupData, "url"> ) => {
    try {
      const { data } = await getSingleGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    