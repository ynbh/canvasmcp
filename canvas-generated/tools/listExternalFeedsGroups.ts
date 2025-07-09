
import { tool } from "ai";
import { listExternalFeedsGroupsDataSchema } from "./aitm.schema.ts";
import { listExternalFeedsGroups, ListExternalFeedsGroupsData } from "..";

export default tool({
  description: `
  List external feeds
Returns the paginated list of External Feeds this course or group.
    `,
  parameters: listExternalFeedsGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListExternalFeedsGroupsData, "url"> ) => {
    try {
      const { data } = await listExternalFeedsGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    