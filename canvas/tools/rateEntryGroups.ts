
import { tool } from "ai";
import { rateEntryGroupsDataSchema } from "./aitm.schema.ts";
import { rateEntryGroups, RateEntryGroupsData } from "..";

export default tool({
  description: `
  Rate entry
Rate a discussion entry.

On success, the response will be 204 No Content with an empty
body.
    `,
  parameters: rateEntryGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<RateEntryGroupsData, "url"> ) => {
    try {
      const { data } = await rateEntryGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    