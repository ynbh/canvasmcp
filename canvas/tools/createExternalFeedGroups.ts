
import { tool } from "ai";
import { createExternalFeedGroupsDataSchema } from "./aitm.schema.ts";
import { createExternalFeedGroups, CreateExternalFeedGroupsData } from "..";

export default tool({
  description: `
  Create an external feed
Create a new external feed for the course or group.
    `,
  parameters: createExternalFeedGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateExternalFeedGroupsData, "url"> ) => {
    try {
      const { data } = await createExternalFeedGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    