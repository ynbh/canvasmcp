
import { tool } from "ai";
import { listConferencesGroupsDataSchema } from "./aitm.schema.ts";
import { listConferencesGroups, ListConferencesGroupsData } from "..";

export default tool({
  description: `
  List conferences
Retrieve the paginated list of conferences for this context

This API returns a
JSON object containing the list of conferences,
the key for the list of conferences is "conferences"
    `,
  parameters: listConferencesGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListConferencesGroupsData, "url"> ) => {
    try {
      const { data } = await listConferencesGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    